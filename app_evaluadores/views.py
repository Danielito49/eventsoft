from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from app_usuarios.permisos import es_evaluador
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from .models import Evaluador, Criterio, Calificacion, EvaluadorEvento, CalificacionProyecto
from app_eventos.models import Evento
from app_participantes.models import ParticipanteEvento, Participante, ProyectoGrupal
from app_usuarios.models import Usuario
import os


def calcular_y_guardar_nota_general(participante, evento):
    """
    Calcula la nota general ponderada de un participante en un evento
    y la guarda en el campo par_eve_valor de ParticipanteEvento
    """
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    peso_total = sum(c.cri_peso for c in criterios) or 1
    
    # Obtener todas las calificaciones del participante en este evento
    calificaciones = Calificacion.objects.filter(
        participante=participante,
        criterio__cri_evento_fk=evento
    ).select_related('criterio')
    
    # Agrupar por evaluador para calcular el promedio de cada uno
    evaluadores_ids = set(c.evaluador_id for c in calificaciones)
    num_evaluadores = len(evaluadores_ids)
    
    if num_evaluadores > 0:
        # Calcular puntaje ponderado promedio
        puntaje_ponderado = sum(
            c.cal_valor * c.criterio.cri_peso for c in calificaciones
        ) / (peso_total * num_evaluadores)
        
        # Guardar en ParticipanteEvento
        participante_evento = ParticipanteEvento.objects.get(
            participante=participante,
            evento=evento
        )
        participante_evento.par_eve_valor = round(puntaje_ponderado, 2)
        participante_evento.save()
        
        return puntaje_ponderado
    
    return 0


def calcular_y_guardar_nota_proyecto(proyecto):
    """
    Calcula la nota general ponderada de un proyecto grupal y la guarda.
    También actualiza la nota de todos los integrantes del proyecto.
    """
    evento = proyecto.evento
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    peso_total = sum(c.cri_peso for c in criterios) or 1
    
    # Obtener todas las calificaciones del proyecto en este evento
    calificaciones = CalificacionProyecto.objects.filter(
        proyecto=proyecto,
        criterio__cri_evento_fk=evento
    ).select_related('criterio')
    
    # Agrupar por evaluador para calcular el promedio de cada uno
    evaluadores_ids = set(c.evaluador_id for c in calificaciones)
    num_evaluadores = len(evaluadores_ids)
    
    if num_evaluadores > 0:
        # Calcular puntaje ponderado promedio
        puntaje_ponderado = sum(
            c.cal_valor * c.criterio.cri_peso for c in calificaciones
        ) / (peso_total * num_evaluadores)
        
        nota_final = round(puntaje_ponderado, 2)
        
        # Guardar en ProyectoGrupal
        proyecto.nota_proyecto = nota_final
        proyecto.save()
        
        # Actualizar la nota de todos los integrantes del proyecto
        ParticipanteEvento.objects.filter(
            proyecto_grupal=proyecto,
            evento=evento
        ).update(par_eve_valor=nota_final)
        
        return nota_final
    
    return 0


def obtener_puesto_participante(participante, evento):
    """
    Obtiene el puesto de un participante en un evento basado en su nota
    """
    # Obtener todas las participaciones del evento ordenadas por nota
    participaciones = ParticipanteEvento.objects.filter(
        evento=evento,
        par_eve_estado='Aprobado',
        par_eve_valor__isnull=False
    ).order_by('-par_eve_valor')
    
    # Encontrar el puesto del participante
    for i, pe in enumerate(participaciones, 1):
        if pe.participante == participante:
            return i
    
    return None  # No encontrado o sin calificación




@login_required
@user_passes_test(es_evaluador, login_url='login')
def dashboard_evaluador(request):
    evaluador = request.user.evaluador
    inscripciones = EvaluadorEvento.objects.select_related('evento', 'categoria_evaluacion').filter(evaluador=evaluador)

    # Agregar información sobre archivos disponibles y categoría a cada inscripción
    inscripciones_con_archivos = []
    for inscripcion in inscripciones:
        inscripcion_data = {
            'inscripcion': inscripcion,
            'evento': inscripcion.evento,
            'estado': inscripcion.eva_eve_estado,
            'tiene_memorias': bool(inscripcion.evento.eve_memorias),
            'tiene_info_tecnica': bool(inscripcion.evento.eve_informacion_tecnica),
            'es_multidisciplinario': inscripcion.evento.eve_es_multidisciplinario == 'Si',
            'categoria_evaluacion': inscripcion.categoria_evaluacion,
        }
        inscripciones_con_archivos.append(inscripcion_data)

    return render(request, 'app_evaluadores/dashboard_evaluador.html', {
        'evaluador': evaluador,
        'inscripciones': inscripciones,
        'inscripciones_con_archivos': inscripciones_con_archivos
    })


@login_required
@user_passes_test(es_evaluador, login_url='login')
def gestionar_items(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)
    try:
        evaluador = request.user.evaluador
        inscripcion = EvaluadorEvento.objects.get(evaluador=evaluador, evento=evento)
        if inscripcion.eva_eve_estado != 'Aprobado':
            messages.warning(request, "Tu inscripción como evaluador no ha sido aprobada para este evento.")
            return redirect('dashboard_evaluador')
    except (EvaluadorEvento.DoesNotExist, Evaluador.DoesNotExist):
        messages.error(request, "No estás inscrito como evaluador en este evento.")
        return redirect('dashboard_evaluador')
    criterios = evento.criterios.all()
    peso_total_actual = sum(c.cri_peso for c in criterios if c.cri_peso is not None)
    return render(request, 'gestion_items_evaluador.html', {
        'evento': evento,
        'criterios': criterios,
        'peso_total_actual': peso_total_actual
    })


@login_required
@user_passes_test(es_evaluador, login_url='login')
def agregar_item(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        peso = float(request.POST.get('peso', 0))
        peso_total_actual = sum(c.cri_peso for c in Criterio.objects.filter(cri_evento_fk=eve_id))        
        if peso_total_actual + peso > 100:
            messages.error(request, 'El peso total no puede exceder el 100%.')
            return redirect('gestionar_items_evaluador', eve_id=eve_id)
        Criterio.objects.create(
            cri_descripcion=descripcion,
            cri_peso=peso,
            cri_evento_fk=evento
        )
        messages.success(request, 'Ítem agregado correctamente.')
        return redirect('gestionar_items_evaluador', eve_id=eve_id)
    peso_total_actual = sum(c.cri_peso for c in Criterio.objects.filter(cri_evento_fk=eve_id))
    peso_restante = 100 - peso_total_actual
    return render(request, 'agregar_item_evaluador.html', {
        'evento': evento,
        'peso_total_actual': peso_total_actual,
        'peso_restante': peso_restante
    })

@login_required
@user_passes_test(es_evaluador, login_url='login')
def editar_item(request, criterio_id):
    criterio = get_object_or_404(Criterio, pk=criterio_id)
    peso_total_actual = sum(
        c.cri_peso for c in Criterio.objects.filter(cri_evento_fk=criterio.cri_evento_fk).exclude(pk=criterio.pk)
    )
    peso_restante = 100 - peso_total_actual
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        peso = float(request.POST.get('peso', 0))
        if peso_total_actual + peso > 100:
            messages.error(request, 'El peso total no puede exceder el 100%.')
            return redirect('gestionar_items_evaluador', eve_id=criterio.cri_evento_fk.pk)
        criterio.cri_descripcion = descripcion
        criterio.cri_peso = peso
        criterio.save()
        messages.success(request, 'Ítem editado correctamente.')
        return redirect('gestionar_items_evaluador', eve_id=criterio.cri_evento_fk.pk)
    return render(request, 'editar_item_evaluador.html', {
        'criterio': criterio,
        'peso_total_actual': peso_total_actual,
        'peso_restante': peso_restante,
    })

@login_required
@user_passes_test(es_evaluador, login_url='login')
def eliminar_item(request, criterio_id):
    criterio = get_object_or_404(Criterio, pk=criterio_id)
    evento_id = criterio.cri_evento_fk.pk
    criterio.delete()
    messages.success(request, 'Ítem eliminado correctamente.')
    return redirect('gestionar_items_evaluador', eve_id=evento_id)


@login_required
@user_passes_test(es_evaluador, login_url='login')
def lista_participantes(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)
    try:
        evaluador = request.user.evaluador
        inscripcion = EvaluadorEvento.objects.get(evaluador=evaluador, evento=evento)
    except Evaluador.DoesNotExist:
        messages.warning(request, "No estás registrado como evaluador.")
        return redirect('login_evaluador')
    except EvaluadorEvento.DoesNotExist:
        messages.error(request, "No estás inscrito como evaluador en este evento.")
        return redirect('dashboard_evaluador')
    
    if not evento.criterios.exists():
        messages.warning(request, "Este evento aún no tiene criterios definidos.")
        return redirect('gestionar_items_evaluador', eve_id=eve_id)
    
    # Obtener todos los participantes aprobados
    participantes_evento = ParticipanteEvento.objects.filter(
        evento=evento,
        par_eve_estado='Aprobado'
    ).select_related('participante__usuario', 'proyecto_grupal')
    
    # Separar individuales y grupales
    participantes_individuales = participantes_evento.filter(es_grupal=False)
    
    # Obtener proyectos grupales únicos con sus integrantes
    proyectos_grupales_ids = participantes_evento.filter(es_grupal=True).values_list('proyecto_grupal_id', flat=True).distinct()
    proyectos_grupales = ProyectoGrupal.objects.filter(id__in=proyectos_grupales_ids, estado='Aprobado')
    
    # Para eventos multidisciplinarios, filtrar por categoría del evaluador si aplica
    categoria_evaluador = inscripcion.categoria_evaluacion
    if evento.eve_es_multidisciplinario == 'Si' and categoria_evaluador:
        # Filtrar participantes individuales por categoría
        participantes_individuales = participantes_individuales.filter(categorias=categoria_evaluador)
        # Filtrar proyectos por categoría
        proyectos_grupales = proyectos_grupales.filter(categorias=categoria_evaluador)
    
    # Calificaciones de participantes individuales
    calificaciones_individuales = Calificacion.objects.filter(
        evaluador=evaluador,
        criterio__cri_evento_fk=evento
    ).values_list('participante_id', flat=True).distinct()
    calificados_individuales = set(calificaciones_individuales)
    
    # Calificaciones de proyectos grupales
    calificaciones_proyectos = CalificacionProyecto.objects.filter(
        evaluador=evaluador,
        criterio__cri_evento_fk=evento
    ).values_list('proyecto_id', flat=True).distinct()
    proyectos_calificados = set(calificaciones_proyectos)
    
    # Preparar proyectos con información de integrantes
    proyectos_con_integrantes = []
    for proyecto in proyectos_grupales:
        integrantes = participantes_evento.filter(proyecto_grupal=proyecto)
        proyectos_con_integrantes.append({
            'proyecto': proyecto,
            'integrantes': integrantes,
            'calificado': proyecto.id in proyectos_calificados
        })
    
    context = {
        'participantes_individuales': participantes_individuales,
        'proyectos_con_integrantes': proyectos_con_integrantes,
        'evento': evento,
        'calificados_individuales': calificados_individuales,
        'proyectos_calificados': proyectos_calificados,
        'categoria_evaluador': categoria_evaluador,
        'es_multidisciplinario': evento.eve_es_multidisciplinario == 'Si',
    }
    return render(request, 'lista_participantes_evaluador.html', context)


@login_required
@user_passes_test(es_evaluador, login_url='login')
def calificar_participante(request, eve_id, participante_id):
    evento = get_object_or_404(Evento, pk=eve_id)
    try:
        evaluador = request.user.evaluador
        inscripcion = EvaluadorEvento.objects.get(evaluador=evaluador, evento=evento)
        if inscripcion.eva_eve_estado != 'Aprobado':
            messages.warning(request, "Tu inscripción como evaluador aún no ha sido aprobada para este evento.")
            return redirect('dashboard_evaluador')
    except (EvaluadorEvento.DoesNotExist, Evaluador.DoesNotExist):
        messages.error(request, "No estás inscrito como evaluador en este evento.")
        return redirect('dashboard_evaluador')
    participante = get_object_or_404(Participante, pk=participante_id)
    participacion = ParticipanteEvento.objects.filter(
        evento=evento,
        participante=participante,
        par_eve_estado='Aprobado'
    ).first()
    if not participacion:
        messages.error(request, "Este participante no está aprobado para ser calificado en este evento.")
        return redirect('lista_participantes_evaluador', eve_id=eve_id)
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    evaluador = request.user.evaluador
    if request.method == 'POST':
        for criterio in criterios:
            valor = request.POST.get(f'criterio_{criterio.cri_id}')
            if valor:
                try:
                    valor_int = int(valor)
                    if 1 <= valor_int <= 5:
                        calificacion, created = Calificacion.objects.get_or_create(
                            evaluador=evaluador,
                            criterio=criterio,
                            participante=participante,
                            defaults={'cal_valor': valor_int}
                        )
                        if not created:
                            calificacion.cal_valor = valor_int
                            calificacion.save()
                    else:
                        messages.error(request, f"El valor de '{criterio.cri_descripcion}' debe estar entre 1 y 5.")
                        return redirect(request.path)
                except ValueError:
                    messages.error(request, f"Valor inválido para '{criterio.cri_descripcion}'.")
                    return redirect(request.path)
        
        # Calcular y guardar la nota general del participante
        calcular_y_guardar_nota_general(participante, evento)
        
        messages.success(request, "Calificaciones guardadas exitosamente.")
        return redirect('lista_participantes_evaluador', eve_id=eve_id)

    return render(request, 'formulario_calificacion.html', {
        'criterios': criterios,
        'participante': participante,
        'evento': evento,
    })


@login_required
@user_passes_test(es_evaluador, login_url='login')
def calificar_proyecto(request, eve_id, proyecto_id):
    """Vista para calificar un proyecto grupal - la nota se aplica a todos los integrantes"""
    evento = get_object_or_404(Evento, pk=eve_id)
    try:
        evaluador = request.user.evaluador
        inscripcion = EvaluadorEvento.objects.get(evaluador=evaluador, evento=evento)
        if inscripcion.eva_eve_estado != 'Aprobado':
            messages.warning(request, "Tu inscripción como evaluador aún no ha sido aprobada para este evento.")
            return redirect('dashboard_evaluador')
    except (EvaluadorEvento.DoesNotExist, Evaluador.DoesNotExist):
        messages.error(request, "No estás inscrito como evaluador en este evento.")
        return redirect('dashboard_evaluador')
    
    proyecto = get_object_or_404(ProyectoGrupal, pk=proyecto_id, evento=evento)
    
    # Verificar que el proyecto esté aprobado (al menos un integrante aprobado)
    integrantes = ParticipanteEvento.objects.filter(
        evento=evento,
        proyecto_grupal=proyecto,
        par_eve_estado='Aprobado'
    ).select_related('participante__usuario')
    
    if not integrantes.exists():
        messages.error(request, "Este proyecto no tiene integrantes aprobados para ser calificado.")
        return redirect('lista_participantes_evaluador', eve_id=eve_id)
    
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    
    if request.method == 'POST':
        for criterio in criterios:
            valor = request.POST.get(f'criterio_{criterio.cri_id}')
            if valor:
                try:
                    valor_int = int(valor)
                    if 1 <= valor_int <= 5:
                        calificacion, created = CalificacionProyecto.objects.get_or_create(
                            evaluador=evaluador,
                            criterio=criterio,
                            proyecto=proyecto,
                            defaults={'cal_valor': valor_int}
                        )
                        if not created:
                            calificacion.cal_valor = valor_int
                            calificacion.save()
                    else:
                        messages.error(request, f"El valor de '{criterio.cri_descripcion}' debe estar entre 1 y 5.")
                        return redirect(request.path)
                except ValueError:
                    messages.error(request, f"Valor inválido para '{criterio.cri_descripcion}'.")
                    return redirect(request.path)
        
        # Calcular y guardar la nota del proyecto (se aplica a todos los integrantes)
        calcular_y_guardar_nota_proyecto(proyecto)
        
        messages.success(request, f"Calificaciones guardadas para el proyecto '{proyecto.nombre_proyecto}' y aplicadas a todos los integrantes.")
        return redirect('lista_participantes_evaluador', eve_id=eve_id)

    return render(request, 'formulario_calificacion_proyecto.html', {
        'criterios': criterios,
        'proyecto': proyecto,
        'integrantes': integrantes,
        'evento': evento,
    })


@login_required
@user_passes_test(es_evaluador, login_url='login')
def ver_tabla_posiciones(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)
    try:
        evaluador = request.user.evaluador
        inscripcion = EvaluadorEvento.objects.get(evaluador=evaluador, evento=evento)
        if inscripcion.eva_eve_estado != 'Aprobado':
            messages.warning(request, "Tu inscripción a este evento aún no ha sido aprobada.")
            return redirect('dashboard_evaluador')
    except (EvaluadorEvento.DoesNotExist, Evaluador.DoesNotExist):
        messages.error(request, "No estás inscrito en este evento.")
        return redirect('dashboard_evaluador')
    
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    peso_total = sum(c.cri_peso for c in criterios) or 1
    
    # Obtener todos los participantes aprobados
    participantes_evento = ParticipanteEvento.objects.filter(
        evento=evento,
        par_eve_estado='Aprobado'
    ).select_related('participante__usuario', 'proyecto_grupal')
    
    # Separar individuales y grupales
    participantes_individuales = participantes_evento.filter(es_grupal=False)
    
    # Proyectos grupales con sus integrantes
    proyectos_ids = participantes_evento.filter(es_grupal=True).values_list('proyecto_grupal_id', flat=True).distinct()
    proyectos = ProyectoGrupal.objects.filter(id__in=proyectos_ids)
    
    # Posiciones de proyectos grupales
    posiciones_proyectos = []
    for proyecto in proyectos:
        integrantes = participantes_evento.filter(proyecto_grupal=proyecto)
        
        if proyecto.nota_proyecto is not None:
            puntaje = proyecto.nota_proyecto
        else:
            # Calcular si no está guardada
            calificaciones = CalificacionProyecto.objects.filter(
                proyecto=proyecto,
                criterio__cri_evento_fk=evento
            ).select_related('criterio')
            evaluadores_ids = set(c.evaluador_id for c in calificaciones)
            num_evaluadores = len(evaluadores_ids)
            if num_evaluadores > 0:
                puntaje = sum(
                    c.cal_valor * c.criterio.cri_peso for c in calificaciones
                ) / (peso_total * num_evaluadores)
                puntaje = round(puntaje, 2)
                proyecto.nota_proyecto = puntaje
                proyecto.save()
            else:
                puntaje = 0
        
        posiciones_proyectos.append({
            'proyecto': proyecto,
            'integrantes': list(integrantes),
            'puntaje': puntaje
        })
    
    posiciones_proyectos.sort(key=lambda x: x['puntaje'], reverse=True)
    
    # Posiciones de participantes individuales
    posiciones_individuales = []
    for pe in participantes_individuales:
        participante = pe.participante
        
        if pe.par_eve_valor is not None:
            puntaje = pe.par_eve_valor
        else:
            calificaciones = Calificacion.objects.filter(
                participante=participante,
                criterio__cri_evento_fk=evento
            ).select_related('criterio')
            evaluadores_ids = set(c.evaluador_id for c in calificaciones)
            num_evaluadores = len(evaluadores_ids)
            if num_evaluadores > 0:
                puntaje = sum(
                    c.cal_valor * c.criterio.cri_peso for c in calificaciones
                ) / (peso_total * num_evaluadores)
                puntaje = round(puntaje, 2)
                pe.par_eve_valor = puntaje
                pe.save()
            else:
                puntaje = 0
        
        posiciones_individuales.append({
            'participante': participante,
            'puntaje': puntaje
        })
    
    posiciones_individuales.sort(key=lambda x: x['puntaje'], reverse=True)
    
    return render(request, 'tabla_posiciones_evaluador.html', {
        'evento': evento,
        'posiciones_proyectos': posiciones_proyectos,
        'posiciones_individuales': posiciones_individuales,
        'tiene_proyectos': len(posiciones_proyectos) > 0,
        'tiene_individuales': len(posiciones_individuales) > 0,
    })


@login_required
@user_passes_test(es_evaluador, login_url='login')
def informacion_detallada(request, eve_id):   
    evaluador = request.user.evaluador
    evento = get_object_or_404(Evento, pk=eve_id)
    try:
        evaluador = request.user.evaluador
        inscripcion = EvaluadorEvento.objects.get(evaluador=evaluador, evento=evento)
        if inscripcion.eva_eve_estado != 'Aprobado':
            messages.warning(request, "No tienes acceso a este evento porque tu inscripción no está aprobada.")
            return redirect('dashboard_evaluador')
    except (EvaluadorEvento.DoesNotExist, Evaluador.DoesNotExist):
        messages.error(request, "No estás inscrito en este evento.")
        return redirect('dashboard_evaluador')
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    total_criterios = criterios.count()
    participantes_evento = ParticipanteEvento.objects.filter(
        evento=evento,
        par_eve_estado='Aprobado'
    ).select_related('participante__usuario')
    participantes_info = []
    for pe in participantes_evento:
        participante = pe.participante
        calificaciones_actual = Calificacion.objects.filter(
            evaluador=evaluador,
            participante=participante,
            criterio__cri_evento_fk=evento
        ).select_related('criterio')
        total_aporte = 0
        calificaciones_lista = []
        for c in calificaciones_actual:
            aporte = (c.cal_valor * c.criterio.cri_peso) / 100
            total_aporte += aporte
            calificaciones_lista.append({
                'criterio': c.criterio,
                'cal_valor': c.cal_valor,
                'aporte': round(aporte, 2)
            })
        evaluado = len(calificaciones_lista) == total_criterios
        promedio_ponderado = round(total_aporte, 2) if calificaciones_lista else None
        participantes_info.append({
            'participante': participante,
            'evaluado': evaluado,
            'promedio_ponderado': promedio_ponderado,
            'calificaciones': calificaciones_lista,
            'evaluados': len(calificaciones_lista),
            'total_criterios': total_criterios
        })
    context = {
        'evaluador': evaluador,
        'evento': evento,
        'criterios': criterios,
        'participantes_info': participantes_info
    }
    return render(request, 'info_detallada_evaluador.html', context)


@login_required
@user_passes_test(es_evaluador, login_url='login')
def cancelar_inscripcion_evaluador(request, evento_id):
    evaluador_usuario = request.user
    evento = get_object_or_404(Evento, pk=evento_id)
    evaluador = evaluador_usuario.evaluador
    inscripcion = get_object_or_404(EvaluadorEvento, evaluador=evaluador, evento=evento)
    if inscripcion.eva_eve_estado != "Pendiente":
        messages.error(request, "No puedes cancelar la inscripción porque ya fue aprobada.")
        return redirect('dashboard_evaluador')
    if request.method == 'POST':
        inscripcion.delete()
        otros_eventos = EvaluadorEvento.objects.filter(evaluador=evaluador).count()
        if otros_eventos == 0:
            Evaluador.objects.filter(usuario=evaluador_usuario).delete()
            usuario_username = evaluador_usuario.username
            evaluador_usuario.delete()
            messages.success(request, f"Se canceló tu inscripción y se eliminó el usuario '{usuario_username}' porque no estaba en otros eventos.")
            return redirect('login')
        messages.success(request, "Inscripción cancelada con éxito.")
        return redirect('dashboard_evaluador')
    return render(request, 'confirmar_cancelacion.html', {
        'evento': evento
    })

@login_required
@user_passes_test(es_evaluador, login_url='login')
def modificar_inscripcion_evaluador(request, evento_id):
    usuario = request.user
    evento = get_object_or_404(Evento, pk=evento_id)
    evaluador = usuario.evaluador
    inscripcion = get_object_or_404(EvaluadorEvento, evaluador=evaluador, evento=evento)
    if inscripcion.eva_eve_estado != "Pendiente":
        messages.error(request, "Solo puedes modificar la inscripción si está en estado Pendiente.")
        return redirect('dashboard_evaluador')
    if request.method == "POST":
        usuario.first_name = request.POST.get("eva_nombres")
        usuario.last_name = request.POST.get("eva_apellidos")
        usuario.email = request.POST.get("eva_correo")
        usuario.telefono = request.POST.get("eva_telefono")
        usuario.documento = request.POST.get("eva_id")
        usuario.save()
        archivo = request.FILES.get('documentacion')
        if archivo:
            inscripcion.eva_eve_qr = archivo
            inscripcion.save()
        messages.success(request, "Información actualizada correctamente.")
        return redirect('dashboard_evaluador')
    return render(request, 'modificar_inscripcion.html', {
        'evento': evento,
        'usuario': usuario,
        'inscripcion': inscripcion
    })


@login_required
@user_passes_test(es_evaluador, login_url='login')
def descargar_memorias_evaluador(request, evento_id):
    """Vista para descargar las memorias de un evento como evaluador"""
    evento = get_object_or_404(Evento, eve_id=evento_id)
    evaluador = request.user.evaluador
    
    # Verificar que el evaluador esté inscrito en el evento
    inscripcion = get_object_or_404(EvaluadorEvento, evaluador=evaluador, evento=evento)
    
    # Solo permitir si el estado no es "Pendiente"
    if inscripcion.eva_eve_estado == 'Pendiente':
        messages.error(request, "No puedes descargar memorias mientras tu inscripción esté pendiente.")
        return redirect('dashboard_evaluador')
    
    # Verificar que el archivo de memorias exista
    if not evento.eve_memorias:
        messages.error(request, "Este evento no tiene memorias disponibles para descargar.")
        return redirect('dashboard_evaluador')
    
    # Verificar que el archivo físico exista
    if not os.path.exists(evento.eve_memorias.path):
        messages.error(request, "El archivo de memorias no se encuentra disponible.")
        return redirect('dashboard_evaluador')
    
    try:
        response = FileResponse(
            open(evento.eve_memorias.path, 'rb'),
            as_attachment=True,
            filename=f"Memorias_{evento.eve_nombre}_{evento.eve_memorias.name.split('/')[-1]}"
        )
        return response
    except Exception as e:
        messages.error(request, "Error al descargar el archivo de memorias.")
        return redirect('dashboard_evaluador')


@login_required
@user_passes_test(es_evaluador, login_url='login')
def descargar_informacion_tecnica_evaluador(request, evento_id):
    """Vista para descargar la información técnica de un evento como evaluador"""
    evento = get_object_or_404(Evento, eve_id=evento_id)
    evaluador = request.user.evaluador
    
    # Verificar que el evaluador esté inscrito en el evento
    inscripcion = get_object_or_404(EvaluadorEvento, evaluador=evaluador, evento=evento)
    
    # Solo permitir si el estado no es "Pendiente"
    if inscripcion.eva_eve_estado == 'Pendiente':
        messages.error(request, "No puedes descargar información técnica mientras tu inscripción esté pendiente.")
        return redirect('dashboard_evaluador')
    
    # Verificar que el archivo de información técnica exista
    if not evento.eve_informacion_tecnica:
        messages.error(request, "Este evento no tiene información técnica disponible para descargar.")
        return redirect('dashboard_evaluador')
    
    # Verificar que el archivo físico exista
    if not os.path.exists(evento.eve_informacion_tecnica.path):
        messages.error(request, "El archivo de información técnica no se encuentra disponible.")
        return redirect('dashboard_evaluador')
    
    try:
        response = FileResponse(
            open(evento.eve_informacion_tecnica.path, 'rb'),
            as_attachment=True,
            filename=f"InfoTecnica_{evento.eve_nombre}_{evento.eve_informacion_tecnica.name.split('/')[-1]}"
        )
        return response
    except Exception as e:
        messages.error(request, "Error al descargar el archivo de información técnica.")
        return redirect('dashboard_evaluador')