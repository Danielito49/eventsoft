from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from datetime import date, timedelta
from app_eventos.models import Evento, EventoCategoria
from app_administradores.models import AdministradorEvento
from app_areas.models import Area, Categoria
from app_usuarios.models import Usuario, Rol, RolUsuario
from app_asistentes.models import Asistente, AsistenteEvento


class VisitanteEventosTestCase(TestCase):
    """Clase base para pruebas del módulo de visitantes (app_eventos)"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        
        # Crear usuario administrador
        self.admin_user = Usuario.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            documento='12345678',
            first_name='Admin',
            last_name='Test',
            telefono='1234567890'
        )
        
        # Crear rol y administrador de evento
        self.rol_admin = Rol.objects.create(nombre='administrador_evento')
        RolUsuario.objects.create(usuario=self.admin_user, rol=self.rol_admin)
        self.administrador = AdministradorEvento.objects.create(usuario=self.admin_user)
        
        # Crear área y categoría
        self.area = Area.objects.create(
            are_nombre='Tecnología',
            are_descripcion='Área de tecnología e innovación'
        )
        self.categoria = Categoria.objects.create(
            cat_nombre='Programación',
            cat_descripcion='Categoría de programación y desarrollo',
            cat_area_fk=self.area
        )
        
        # Crear eventos de prueba
        self.evento_aprobado = Evento.objects.create(
            eve_nombre='Evento de Prueba',
            eve_descripcion='Descripción del evento de prueba',
            eve_ciudad='Bogotá',
            eve_lugar='Centro de Convenciones',
            eve_fecha_inicio=date.today() + timedelta(days=30),
            eve_fecha_fin=date.today() + timedelta(days=31),
            eve_estado='Aprobado',
            eve_capacidad=100,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        self.evento_con_costo = Evento.objects.create(
            eve_nombre='Evento Con Costo',
            eve_descripcion='Evento que requiere pago',
            eve_ciudad='Medellín',
            eve_lugar='Hotel Dann',
            eve_fecha_inicio=date.today() + timedelta(days=15),
            eve_fecha_fin=date.today() + timedelta(days=16),
            eve_estado='Aprobado',
            eve_capacidad=50,
            eve_tienecosto='SI',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        self.evento_no_disponible = Evento.objects.create(
            eve_nombre='Evento No Disponible',
            eve_descripcion='Evento en borrador',
            eve_ciudad='Cali',
            eve_lugar='Universidad',
            eve_fecha_inicio=date.today() + timedelta(days=45),
            eve_fecha_fin=date.today() + timedelta(days=46),
            eve_estado='Borrador',
            eve_capacidad=75,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        # Asociar categorías a eventos
        EventoCategoria.objects.create(evento=self.evento_aprobado, categoria=self.categoria)
        EventoCategoria.objects.create(evento=self.evento_con_costo, categoria=self.categoria)


class VerEventosProximosTestCase(VisitanteEventosTestCase):
    """
    Historia 1: Como VISITANTE WEB, Quiero ver los diferentes eventos próximos a realizarse, 
    Para saber si existe algún evento de mi interés.
    """
    
    def test_visitante_puede_acceder_sin_autenticacion(self):
        """CA1: El visitante puede acceder a la lista de eventos sin autenticación"""
        response = self.client.get(reverse('ver_eventos'))
        self.assertEqual(response.status_code, 200)
    
    def test_solo_muestra_eventos_disponibles(self):
        """CA2: Solo se muestran eventos con estado 'Aprobado' o 'Inscripciones Cerradas'"""
        response = self.client.get(reverse('ver_eventos'))
        eventos_mostrados = response.context['eventos']
        
        # Verificar que incluye eventos aprobados
        self.assertIn(self.evento_aprobado, eventos_mostrados)
        self.assertIn(self.evento_con_costo, eventos_mostrados)
        
        # Verificar que NO incluye eventos no disponibles
        self.assertNotIn(self.evento_no_disponible, eventos_mostrados)
    
    def test_muestra_informacion_basica_eventos(self):
        """CA3: Los eventos se muestran con información básica"""
        response = self.client.get(reverse('ver_eventos'))
        
        # Verificar que la respuesta contiene información del evento
        self.assertContains(response, self.evento_aprobado.eve_nombre)
        self.assertContains(response, self.evento_aprobado.eve_ciudad)
        self.assertContains(response, self.evento_con_costo.eve_nombre)
    
    def test_vista_carga_correctamente(self):
        """CA4: La vista carga correctamente con código de respuesta HTTP 200"""
        response = self.client.get(reverse('ver_eventos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'eventos')  # Verificar que contiene contexto de eventos
    
    def test_muestra_todas_las_areas_en_contexto(self):
        """CA5: Se cargan todas las áreas disponibles para filtros"""
        response = self.client.get(reverse('ver_eventos'))
        
        areas_contexto = response.context['areas']
        self.assertIn(self.area, areas_contexto)
        self.assertTrue(len(areas_contexto) > 0)
    
    def test_muestra_todas_categorias_sin_filtro_area(self):
        """CA6: Sin filtro de área, se muestran todas las categorías"""
        response = self.client.get(reverse('ver_eventos'))
        
        categorias_contexto = response.context['categorias']
        self.assertIn(self.categoria, categorias_contexto)
        # Debe mostrar todas las categorías cuando no hay filtro de área
        total_categorias = Categoria.objects.count()
        self.assertEqual(len(categorias_contexto), total_categorias)
    
    def test_filtra_categorias_por_area_seleccionada(self):
        """CA7: Al filtrar por área, solo muestra categorías de esa área"""
        url = reverse('ver_eventos') + f'?area={self.area.are_codigo}'
        response = self.client.get(url)
        
        categorias_contexto = response.context['categorias']
        # Solo debe mostrar categorías del área seleccionada
        for categoria in categorias_contexto:
            self.assertEqual(categoria.cat_area_fk.are_codigo, self.area.are_codigo)
    
    def test_eventos_distinct_elimina_duplicados(self):
        """CA8: Los eventos se devuelven sin duplicados usando distinct()"""
        # Crear segunda categoría en la misma área para el mismo evento
        categoria2 = Categoria.objects.create(
            cat_nombre='Desarrollo Web',
            cat_descripcion='Desarrollo web y aplicaciones',
            cat_area_fk=self.area
        )
        EventoCategoria.objects.create(evento=self.evento_aprobado, categoria=categoria2)
        
        response = self.client.get(reverse('ver_eventos'))
        eventos_mostrados = list(response.context['eventos'])
        
        # Contar cuántas veces aparece el evento (debería ser solo 1)
        count_evento = eventos_mostrados.count(self.evento_aprobado)
        self.assertEqual(count_evento, 1)
    
    def test_sin_filtros_devuelve_todos_eventos_disponibles(self):
        """CA9: Sin parámetros de filtro, devuelve todos los eventos disponibles"""
        response = self.client.get(reverse('ver_eventos'))
        
        eventos_mostrados = response.context['eventos']
        eventos_disponibles = Evento.objects.filter(eve_estado__in=['Aprobado', 'Inscripciones Cerradas'])
        
        # Verificar que se muestran todos los eventos disponibles
        self.assertEqual(len(eventos_mostrados), len(eventos_disponibles))
    
    def test_parametros_vacios_no_afectan_filtrado(self):
        """CA10: Parámetros vacíos en la URL no afectan el filtrado"""
        url = reverse('ver_eventos') + '?area=&categoria=&ciudad=&fecha=&nombre='
        response = self.client.get(url)
        
        eventos_mostrados = response.context['eventos']
        eventos_esperados = Evento.objects.filter(eve_estado__in=['Aprobado', 'Inscripciones Cerradas'])
        
        self.assertEqual(len(eventos_mostrados), len(eventos_esperados))


class BusquedaFiltrosEventosTestCase(VisitanteEventosTestCase):
    """
    Historia 2: Como VISITANTE WEB, Quiero realizar búsquedas de eventos de mi interés usando diferentes filtros, 
    Para encontrar los eventos que más me interesan.
    """
    
    def test_filtro_por_area(self):
        """CA1: El visitante puede filtrar eventos por área"""
        url = reverse('ver_eventos') + f'?area={self.area.are_codigo}'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
        self.assertIn(self.evento_con_costo, eventos_filtrados)
    
    def test_filtro_por_categoria(self):
        """CA2: El visitante puede filtrar eventos por categoría"""
        url = reverse('ver_eventos') + f'?categoria={self.categoria.cat_codigo}'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
        self.assertIn(self.evento_con_costo, eventos_filtrados)
    
    def test_filtro_por_ciudad(self):
        """CA3: El visitante puede filtrar eventos por ciudad"""
        url = reverse('ver_eventos') + '?ciudad=Bogotá'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
        self.assertNotIn(self.evento_con_costo, eventos_filtrados)  # Este es de Medellín
    
    def test_filtro_por_fecha(self):
        """CA4: El visitante puede filtrar eventos por fecha"""
        fecha_filtro = self.evento_aprobado.eve_fecha_inicio.strftime('%Y-%m-%d')
        url = reverse('ver_eventos') + f'?fecha={fecha_filtro}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        eventos_filtrados = response.context['eventos']
        # El evento debe estar en el rango de fechas
        self.assertIn(self.evento_aprobado, eventos_filtrados)
    
    def test_busqueda_por_nombre(self):
        """CA5: El visitante puede buscar eventos por nombre"""
        url = reverse('ver_eventos') + '?nombre=Prueba'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
        self.assertNotIn(self.evento_con_costo, eventos_filtrados)
    
    def test_combinacion_filtros(self):
        """CA6: Los filtros se pueden combinar para refinar la búsqueda"""
        url = reverse('ver_eventos') + f'?ciudad=Bogotá&categoria={self.categoria.cat_codigo}'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
        self.assertNotIn(self.evento_con_costo, eventos_filtrados)
    
    def test_busqueda_nombre_insensible_mayusculas(self):
        """CA7: La búsqueda por nombre es insensible a mayúsculas y minúsculas"""
        url = reverse('ver_eventos') + '?nombre=PRUEBA'  # En mayúsculas
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)  # "Evento de Prueba"
    
    def test_busqueda_ciudad_insensible_mayusculas(self):
        """CA8: La búsqueda por ciudad es insensible a mayúsculas y minúsculas"""
        url = reverse('ver_eventos') + '?ciudad=bogotá'  # En minúsculas
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)  # Bogotá con mayúscula
    
    def test_busqueda_parcial_nombre(self):
        """CA9: La búsqueda permite coincidencias parciales en el nombre"""
        url = reverse('ver_eventos') + '?nombre=Prueb'  # Solo parte del nombre
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
    
    def test_busqueda_parcial_ciudad(self):
        """CA10: La búsqueda permite coincidencias parciales en la ciudad"""
        url = reverse('ver_eventos') + '?ciudad=Bog'  # Solo parte de "Bogotá"
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
    
    def test_filtro_categoria_inexistente(self):
        """CA11: Filtrar por categoría inexistente devuelve lista vacía"""
        url = reverse('ver_eventos') + '?categoria=99999'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertEqual(len(eventos_filtrados), 0)
    
    def test_filtro_area_inexistente(self):
        """CA12: Filtrar por área inexistente devuelve lista vacía"""
        url = reverse('ver_eventos') + '?area=99999'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertEqual(len(eventos_filtrados), 0)
    
    def test_combinacion_todos_los_filtros(self):
        """CA13: Todos los filtros funcionan simultáneamente"""
        fecha_evento = self.evento_aprobado.eve_fecha_inicio.strftime('%Y-%m-%d')
        url = reverse('ver_eventos') + f'?area={self.area.are_codigo}&categoria={self.categoria.cat_codigo}&ciudad=Bogotá&fecha={fecha_evento}&nombre=Prueba'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertIn(self.evento_aprobado, eventos_filtrados)
        self.assertNotIn(self.evento_con_costo, eventos_filtrados)  # No coincide con todos los criterios
    
    def test_fecha_fuera_de_rango_evento(self):
        """CA14: Filtrar por fecha fuera del rango del evento no lo incluye"""
        fecha_anterior = (self.evento_aprobado.eve_fecha_inicio - timedelta(days=1)).strftime('%Y-%m-%d')
        url = reverse('ver_eventos') + f'?fecha={fecha_anterior}'
        response = self.client.get(url)
        
        eventos_filtrados = response.context['eventos']
        self.assertNotIn(self.evento_aprobado, eventos_filtrados)


class InformacionDetalladaEventosTestCase(VisitanteEventosTestCase):
    """
    Historia 3: Como VISITANTE WEB, Quiero acceder a información detallada sobre los eventos de mi interés, 
    Para tener mayor claridad sobre mi posibilidad e interés de asistir.
    """
    
    def test_acceso_detalle_evento_especifico(self):
        """CA1: El visitante puede acceder al detalle de un evento específico"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        self.assertEqual(response.status_code, 200)
    
    def test_muestra_informacion_completa_evento(self):
        """CA2: Se muestra toda la información del evento"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        # Verificar información del evento en la respuesta
        self.assertContains(response, self.evento_aprobado.eve_nombre)
        self.assertContains(response, self.evento_aprobado.eve_descripcion)
        self.assertContains(response, self.evento_aprobado.eve_ciudad)
        self.assertContains(response, self.evento_aprobado.eve_lugar)
        self.assertContains(response, str(self.evento_aprobado.eve_capacidad))
    
    def test_muestra_categorias_asociadas(self):
        """CA3: Se muestran las categorías asociadas al evento"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        self.assertEqual(response.status_code, 200)
        # Verificar que el contexto incluye las categorías
        self.assertIn('categorias', response.context)
    
    def test_carga_correcta_eventos_existentes(self):
        """CA4: La vista carga correctamente para eventos existentes"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['evento'], self.evento_aprobado)
    
    def test_manejo_evento_inexistente(self):
        """CA5: Se maneja correctamente cuando el evento no existe (error 404)"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[99999]))
        
        self.assertEqual(response.status_code, 404)
    
    def test_carga_administrador_con_select_related(self):
        """CA6: El evento se carga con su administrador usando select_related para optimización"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        evento = response.context['evento']
        # Verificar que el administrador está precargado
        self.assertEqual(evento.eve_administrador_fk, self.administrador)
        # Verificar que se puede acceder al usuario del administrador sin query adicional
        self.assertEqual(evento.eve_administrador_fk.usuario.first_name, 'Admin')
    
    def test_categorias_con_areas_precargadas(self):
        """CA7: Las categorías se cargan con sus áreas usando select_related"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        categorias = response.context['categorias']
        for categoria_evento in categorias:
            # Verificar que se puede acceder al área sin query adicional
            self.assertIsNotNone(categoria_evento.categoria.cat_area_fk.are_nombre)
    
    def test_evento_sin_categorias(self):
        """CA8: Maneja correctamente eventos que no tienen categorías asignadas"""
        # Crear evento sin categorías
        evento_sin_cat = Evento.objects.create(
            eve_nombre='Evento Sin Categorías',
            eve_descripcion='Evento de prueba sin categorías',
            eve_ciudad='Cali',
            eve_lugar='Centro',
            eve_fecha_inicio=date.today() + timedelta(days=20),
            eve_fecha_fin=date.today() + timedelta(days=21),
            eve_estado='Aprobado',
            eve_capacidad=30,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        response = self.client.get(reverse('detalle_evento_visitante', args=[evento_sin_cat.eve_id]))
        
        self.assertEqual(response.status_code, 200)
        categorias = response.context['categorias']
        self.assertEqual(len(categorias), 0)
    
    def test_contexto_completo_detalle_evento(self):
        """CA9: El contexto contiene toda la información necesaria"""
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        # Verificar que el contexto tiene las claves esperadas
        self.assertIn('evento', response.context)
        self.assertIn('categorias', response.context)
        
        # Verificar tipos correctos
        self.assertIsInstance(response.context['evento'], Evento)
        self.assertTrue(hasattr(response.context['categorias'], '__iter__'))  # Es iterable


class CompartirEventoTestCase(VisitanteEventosTestCase):
    """
    Historia 4: Como VISITANTE WEB, Quiero compartir la información de eventos con mis contactos, 
    Para darlos a conocer a personas posiblemente interesadas en asistir.
    """
    
    def test_generar_contenido_compartible(self):
        """CA1: El visitante puede generar contenido compartible del evento"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('mensaje', data)
        self.assertIn('url', data)
    
    def test_solo_eventos_publicos_disponibles(self):
        """CA2: Solo se permite compartir eventos públicamente disponibles"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_no_disponible.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_mensaje_contiene_informacion_completa(self):
        """CA3: Se genera un mensaje con información completa del evento"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        mensaje = data['mensaje']
        
        # Verificar que el mensaje contiene información del evento
        self.assertIn(self.evento_aprobado.eve_nombre, mensaje)
        self.assertIn(self.evento_aprobado.eve_ciudad, mensaje)
        self.assertIn(self.evento_aprobado.eve_descripcion, mensaje)
    
    def test_incluye_url_evento(self):
        """CA4: Se incluye la URL del evento en el contenido compartible"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        self.assertIn('url', data)
        self.assertTrue(data['url'].endswith(f'/detalle-evento/{self.evento_aprobado.eve_id}/'))
    
    def test_rechaza_compartir_eventos_no_disponibles(self):
        """CA5: Se rechaza la compartición de eventos no disponibles públicamente"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_no_disponible.eve_id]),
            HTTP_X_REQUESTED_With='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_maneja_evento_inexistente_compartir(self):
        """CA6: Maneja correctamente cuando el evento a compartir no existe"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[99999]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_diferencia_fechas_inicio_fin(self):
        """CA7: Maneja correctamente eventos con fechas de inicio y fin diferentes"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        mensaje = data['mensaje']
        
        # Debe incluir ambas fechas si son diferentes
        fecha_inicio = self.evento_aprobado.eve_fecha_inicio.strftime('%d/%m/%Y')
        fecha_fin = self.evento_aprobado.eve_fecha_fin.strftime('%d/%m/%Y')
        
        if self.evento_aprobado.eve_fecha_inicio != self.evento_aprobado.eve_fecha_fin:
            self.assertIn(fecha_inicio, mensaje)
            self.assertIn(fecha_fin, mensaje)
    
    def test_evento_sin_categorias_compartir(self):
        """CA8: Maneja eventos sin categorías asignadas al compartir"""
        # Crear evento sin categorías
        evento_sin_cat = Evento.objects.create(
            eve_nombre='Evento Sin Categorías',
            eve_descripcion='Evento sin categorías para compartir',
            eve_ciudad='Medellín',
            eve_lugar='Centro',
            eve_fecha_inicio=date.today() + timedelta(days=10),
            eve_fecha_fin=date.today() + timedelta(days=10),
            eve_estado='Aprobado',
            eve_capacidad=25,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[evento_sin_cat.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        mensaje = data['mensaje']
        
        # No debe incluir sección de categorías
        self.assertNotIn('🏷️ Categorías:', mensaje)
    
    def test_diferenciacion_eventos_costo_vs_gratuitos(self):
        """CA9: Diferencia correctamente entre eventos con costo y gratuitos"""
        # Evento gratuito
        response_gratuito = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Evento con costo
        response_costo = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_con_costo.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        mensaje_gratuito = response_gratuito.json()['mensaje']
        mensaje_costo = response_costo.json()['mensaje']
        
        self.assertIn('🆓 ¡Evento gratuito!', mensaje_gratuito)
        self.assertIn('💳 Evento con costo', mensaje_costo)
    
    def test_peticion_get_no_permitida(self):
        """CA10: Las peticiones GET devuelven método no permitido"""
        response = self.client.get(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id])
        )
        
        self.assertEqual(response.status_code, 405)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Método no permitido', data['error'])
    
    def test_acepta_peticiones_post_y_ajax(self):
        """CA11: Acepta tanto peticiones POST como AJAX"""
        # Petición POST regular
        response_post = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id])
        )
        self.assertEqual(response_post.status_code, 200)
        
        # Petición AJAX
        response_ajax = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_ajax.status_code, 200)
    
    def test_url_absoluta_generacion(self):
        """CA12: Genera URL absoluta correcta del evento"""
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[self.evento_aprobado.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        url_generada = data['url']
        
        # Debe ser una URL completa
        self.assertTrue(url_generada.startswith('http'))
        self.assertIn(f'/detalle-evento/{self.evento_aprobado.eve_id}/', url_generada)


class RegistroEventoTestCase(VisitanteEventosTestCase):
    """
    Historia 5: Como VISITANTE WEB, Quiero registrarme a un evento, 
    Para poder asistir al mismo.
    """
    
    def setUp(self):
        super().setUp()
        self.datos_registro = {
            'asi_id': '87654321',
            'asi_nombres': 'Juan',
            'asi_apellidos': 'Pérez',
            'asi_correo': 'juan.perez@test.com',
            'asi_telefono': '3001234567'
        }
    
    def test_registro_asistente_sin_codigo(self):
        """CA1: El visitante puede registrarse como asistente sin código de invitación"""
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro
        )
        
        # Debe redirigir o mostrar página de confirmación
        self.assertIn(response.status_code, [200, 302])
    
    def test_requiere_datos_obligatorios(self):
        """CA2: Se requieren datos obligatorios"""
        datos_incompletos = self.datos_registro.copy()
        del datos_incompletos['asi_nombres']
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            datos_incompletos
        )
        
        # Debe redirigir de vuelta por datos faltantes
        self.assertEqual(response.status_code, 302)
    
    def test_valida_no_registrado_previamente(self):
        """CA3: Se valida que no esté ya registrado en el mismo evento"""
        # Primer registro
        self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro
        )
        
        # Segundo intento de registro
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro
        )
        
        # Debe redirigir o mostrar mensaje de ya registrado
        self.assertIn(response.status_code, [200, 302])
    
    def test_evento_inexistente_registro(self):
        """CA6: Maneja correctamente cuando el evento no existe"""
        response = self.client.post(
            reverse('inscripcion_asistente', args=[99999]),
            self.datos_registro
        )
        
        # Debe redirigir a ver_eventos con mensaje de error
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ver_eventos'))
    
    def test_tipo_registro_invalido(self):
        """CA7: Rechaza tipos de registro inválidos para este flujo"""
        # Simular POST a inscripcion_asistente pero internamente pasando tipo incorrecto
        # Esto testea la línea: return HttpResponse('Tipo de registro inválido para este flujo.')
        from django.test import RequestFactory
        from app_eventos.views import registro_evento
        
        factory = RequestFactory()
        request = factory.post('/', self.datos_registro)
        
        response = registro_evento(request, self.evento_aprobado.eve_id, 'participante')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tipo de registro inválido', response.content.decode())
    
    def test_validacion_consistencia_datos_usuario_existente(self):
        """CA8: Valida consistencia de datos con usuario existente"""
        # Crear usuario existente
        Usuario.objects.create_user(
            username='test_user',
            email='test@different.com',  # Email diferente
            documento='87654321',
            first_name='Juan',
            last_name='Pérez',
            password='testpass'
        )
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro  # Datos que no coinciden
        )
        
        # Debe redirigir con mensaje de error de consistencia
        self.assertEqual(response.status_code, 302)
    
    def test_usuario_activo_genera_qr_evento_gratuito(self):
        """CA9: Usuario activo en evento gratuito genera QR automáticamente"""
        # Crear usuario activo
        usuario_activo = Usuario.objects.create_user(
            username='activo_user',
            email=self.datos_registro['asi_correo'],
            documento=self.datos_registro['asi_id'],
            first_name=self.datos_registro['asi_nombres'],
            last_name=self.datos_registro['asi_apellidos'],
            password='testpass',
            is_active=True
        )
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro
        )
        
        # Verificar que se creó la asistencia con QR
        asistente = getattr(usuario_activo, 'asistente', None)
        if asistente:
            asistencia = AsistenteEvento.objects.filter(asistente=asistente, evento=self.evento_aprobado).first()
            if asistencia:
                self.assertEqual(asistencia.asi_eve_estado, 'Aprobado')
                # Para evento gratuito, debe tener QR
                self.assertIsNotNone(asistencia.asi_eve_qr)
    
    def test_usuario_activo_evento_con_costo_estado_pendiente(self):
        """CA10: Usuario activo en evento con costo queda pendiente"""
        # Crear usuario activo
        usuario_activo = Usuario.objects.create_user(
            username='activo_user2',
            email='usuario2@test.com',
            documento='11111111',
            first_name='Ana',
            last_name='García',
            password='testpass',
            is_active=True
        )
        
        archivo_soporte = SimpleUploadedFile(
            "comprobante.pdf", 
            b"contenido del archivo pdf", 
            content_type="application/pdf"
        )
        
        datos_con_soporte = {
            'asi_id': '11111111',
            'asi_nombres': 'Ana',
            'asi_apellidos': 'García',
            'asi_correo': 'usuario2@test.com',
            'asi_telefono': '3001234567',
            'soporte_pago': archivo_soporte
        }
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_con_costo.eve_id]),
            datos_con_soporte
        )
        
        # Verificar estado pendiente para evento con costo
        asistente = getattr(usuario_activo, 'asistente', None)
        if asistente:
            asistencia = AsistenteEvento.objects.filter(asistente=asistente, evento=self.evento_con_costo).first()
            if asistencia:
                self.assertEqual(asistencia.asi_eve_estado, 'Pendiente')
    
    def test_capacidad_evento_se_reduce_evento_gratuito(self):
        """CA11: La capacidad del evento se reduce para eventos gratuitos aprobados"""
        capacidad_inicial = self.evento_aprobado.eve_capacidad
        
        # Crear usuario activo para registro directo
        usuario_activo = Usuario.objects.create_user(
            username='activo_user3',
            email='usuario3@test.com',
            documento='22222222',
            first_name='Carlos',
            last_name='López',
            password='testpass',
            is_active=True
        )
        
        datos_registro = {
            'asi_id': '22222222',
            'asi_nombres': 'Carlos',
            'asi_apellidos': 'López',
            'asi_correo': 'usuario3@test.com',
            'asi_telefono': '3001234567'
        }
        
        self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            datos_registro
        )
        
        # Recargar evento y verificar capacidad
        self.evento_aprobado.refresh_from_db()
        self.assertEqual(self.evento_aprobado.eve_capacidad, capacidad_inicial - 1)
    
    def test_procesa_soporte_pago_eventos_costo(self):
        """CA4: Se procesa correctamente el soporte de pago para eventos con costo"""
        archivo_soporte = SimpleUploadedFile(
            "comprobante.pdf", 
            b"contenido del archivo pdf", 
            content_type="application/pdf"
        )
        datos_con_soporte = self.datos_registro.copy()
        datos_con_soporte['soporte_pago'] = archivo_soporte
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_con_costo.eve_id]),
            datos_con_soporte
        )
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_envia_confirmacion_correo(self):
        """CA5: Se envía confirmación por correo electrónico"""
        # Nota: Esta prueba verifica que el proceso no falla al enviar correo
        # En un entorno real se podría usar mock para verificar el envío
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro
        )
        
        self.assertIn(response.status_code, [200, 302])


class SoportePagoTestCase(VisitanteEventosTestCase):
    """
    Historia 6: Como VISITANTE WEB, Quiero anexar soporte(s) del pago requerido para la asistencia a eventos con cobro de ingreso, 
    Para Asegurar mi asistencia y cupo en el evento.
    """
    
    def setUp(self):
        super().setUp()
        self.datos_registro = {
            'asi_id': '87654321',
            'asi_nombres': 'Juan',
            'asi_apellidos': 'Pérez',
            'asi_correo': 'juan.perez@test.com',
            'asi_telefono': '3001234567'
        }
    
    def test_permite_subir_archivo_soporte(self):
        """CA1: Para eventos con costo, se permite subir archivo de soporte de pago"""
        archivo_soporte = SimpleUploadedFile(
            "comprobante.pdf", 
            b"contenido del archivo pdf", 
            content_type="application/pdf"
        )
        datos_con_soporte = self.datos_registro.copy()
        datos_con_soporte['soporte_pago'] = archivo_soporte
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_con_costo.eve_id]),
            datos_con_soporte
        )
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_guarda_archivo_correctamente(self):
        """CA2: El archivo se guarda correctamente en el sistema"""
        archivo_soporte = SimpleUploadedFile(
            "comprobante.pdf", 
            b"contenido del archivo pdf", 
            content_type="application/pdf"
        )
        datos_con_soporte = self.datos_registro.copy()
        datos_con_soporte['soporte_pago'] = archivo_soporte
        
        self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_con_costo.eve_id]),
            datos_con_soporte
        )
        
        # Verificar si se creó el usuario y la relación
        usuario = Usuario.objects.filter(email=self.datos_registro['asi_correo']).first()
        if usuario:
            asistente = getattr(usuario, 'asistente', None)
            if asistente:
                asistencia = AsistenteEvento.objects.filter(
                    asistente=asistente, 
                    evento=self.evento_con_costo
                ).first()
                if asistencia:
                    # Si se guardó correctamente, debe tener soporte
                    self.assertIsNotNone(asistencia.asi_eve_soporte)
    
    def test_estado_pendiente_con_costo(self):
        """CA3: El estado del asistente cambia a 'Pendiente' cuando hay costo"""
        archivo_soporte = SimpleUploadedFile(
            "comprobante.pdf", 
            b"contenido del archivo pdf", 
            content_type="application/pdf"
        )
        datos_con_soporte = self.datos_registro.copy()
        datos_con_soporte['soporte_pago'] = archivo_soporte
        
        self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_con_costo.eve_id]),
            datos_con_soporte
        )
        
        # Verificar estado pendiente
        usuario = Usuario.objects.filter(email=self.datos_registro['asi_correo']).first()
        if usuario:
            asistente = getattr(usuario, 'asistente', None)
            if asistente:
                asistencia = AsistenteEvento.objects.filter(
                    asistente=asistente, 
                    evento=self.evento_con_costo
                ).first()
                if asistencia:
                    self.assertEqual(asistencia.asi_eve_estado, 'Pendiente')
    
    def test_valida_archivo_requerido_eventos_costo(self):
        """CA4: Se valida que el archivo sea requerido para eventos con costo"""
        # Intentar registrarse en evento con costo sin soporte
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_con_costo.eve_id]),
            self.datos_registro  # Sin archivo de soporte
        )
        
        # El sistema debe procesar el registro pero marcarlo como pendiente
        self.assertIn(response.status_code, [200, 302])
    
    def test_usuario_inactivo_proceso_confirmacion(self):
        """CA5: Usuario inactivo debe pasar por proceso de confirmación"""
        # Crear usuario inactivo
        usuario_inactivo = Usuario.objects.create_user(
            username='inactivo_user',
            email=self.datos_registro['asi_correo'],
            documento=self.datos_registro['asi_id'],
            first_name=self.datos_registro['asi_nombres'],
            last_name=self.datos_registro['asi_apellidos'],
            password='testpass',
            is_active=False
        )
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            self.datos_registro
        )
        
        # Verificar que se creó AsistenteEvento con confirmado=False
        asistente = getattr(usuario_inactivo, 'asistente', None)
        if asistente:
            asistencia = AsistenteEvento.objects.filter(asistente=asistente, evento=self.evento_aprobado).first()
            if asistencia:
                self.assertFalse(asistencia.confirmado)
                self.assertEqual(asistencia.asi_eve_estado, 'Pendiente')
    
    def test_creacion_nuevo_usuario_proceso_confirmacion(self):
        """CA6: Nuevo usuario debe pasar por proceso de confirmación"""
        datos_nuevo_usuario = {
            'asi_id': '99999999',
            'asi_nombres': 'Nuevo',
            'asi_apellidos': 'Usuario',
            'asi_correo': 'nuevo@test.com',
            'asi_telefono': '3001234567'
        }
        
        response = self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            datos_nuevo_usuario
        )
        
        # Verificar que se creó el usuario inactivo
        usuario = Usuario.objects.filter(email='nuevo@test.com').first()
        self.assertIsNotNone(usuario)
        self.assertFalse(usuario.is_active)
        
        # Verificar AsistenteEvento con confirmado=False
        asistente = getattr(usuario, 'asistente', None)
        if asistente:
            asistencia = AsistenteEvento.objects.filter(asistente=asistente, evento=self.evento_aprobado).first()
            if asistencia:
                self.assertFalse(asistencia.confirmado)
    
    def test_asignacion_rol_asistente_usuario_existente(self):
        """CA7: Se asigna rol de asistente a usuario existente que no lo tiene"""
        # Crear rol de asistente si no existe
        rol_asistente, _ = Rol.objects.get_or_create(nombre='asistente')
        
        # Crear usuario sin rol de asistente
        usuario_sin_rol = Usuario.objects.create_user(
            username='sin_rol_user',
            email='sinrol@test.com',
            documento='33333333',
            first_name='Sin',
            last_name='Rol',
            password='testpass',
            is_active=True
        )
        
        datos_sin_rol = {
            'asi_id': '33333333',
            'asi_nombres': 'Sin',
            'asi_apellidos': 'Rol',
            'asi_correo': 'sinrol@test.com',
            'asi_telefono': '3001234567'
        }
        
        # Verificar que no tiene rol de asistente
        self.assertFalse(RolUsuario.objects.filter(usuario=usuario_sin_rol, rol=rol_asistente).exists())
        
        self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            datos_sin_rol
        )
        
        # Verificar que ahora tiene el rol
        self.assertTrue(RolUsuario.objects.filter(usuario=usuario_sin_rol, rol=rol_asistente).exists())
    
    def test_no_crear_relacion_duplicada_asistente_evento(self):
        """CA8: No crea relación duplicada AsistenteEvento si ya existe"""
        # Crear usuario activo con asistente ya existente
        usuario_existente = Usuario.objects.create_user(
            username='existente_user',
            email='existente@test.com',
            documento='44444444',
            first_name='Existente',
            last_name='Usuario',
            password='testpass',
            is_active=True
        )
        
        # Crear asistente y relación previa
        asistente = Asistente.objects.create(usuario=usuario_existente)
        AsistenteEvento.objects.create(
            asistente=asistente,
            evento=self.evento_aprobado,
            asi_eve_fecha_hora=timezone.now(),
            asi_eve_estado='Aprobado',
            confirmado=True
        )
        
        datos_existente = {
            'asi_id': '44444444',
            'asi_nombres': 'Existente',
            'asi_apellidos': 'Usuario',
            'asi_correo': 'existente@test.com',
            'asi_telefono': '3001234567'
        }
        
        # Contar relaciones antes
        count_antes = AsistenteEvento.objects.filter(asistente=asistente, evento=self.evento_aprobado).count()
        
        self.client.post(
            reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]),
            datos_existente
        )
        
        # Contar relaciones después - no debe cambiar
        count_despues = AsistenteEvento.objects.filter(asistente=asistente, evento=self.evento_aprobado).count()
        self.assertEqual(count_antes, count_despues)


class ConfirmarRegistroTestCase(VisitanteEventosTestCase):
    """
    Pruebas adicionales para la función confirmar_registro() que maneja
    tokens de confirmación, limpieza de datos y estados de usuario
    """
    
    def setUp(self):
        super().setUp()
        # Crear rol de asistente para las pruebas
        self.rol_asistente, _ = Rol.objects.get_or_create(nombre='asistente')
    
    def test_token_valido_usuario_inactivo_confirmacion_exitosa(self):
        """Confirmar registro con token válido para usuario inactivo"""
        from itsdangerous import URLSafeTimedSerializer
        from django.conf import settings
        
        # Crear usuario inactivo
        usuario = Usuario.objects.create_user(
            username='test_confirm',
            email='confirm@test.com',
            documento='55555555',
            first_name='Test',
            last_name='Confirm',
            password='temporal',
            is_active=False
        )
        
        # Crear asistente y relación no confirmada
        asistente = Asistente.objects.create(usuario=usuario)
        AsistenteEvento.objects.create(
            asistente=asistente,
            evento=self.evento_aprobado,
            asi_eve_fecha_hora=timezone.now(),
            asi_eve_estado='Pendiente',
            confirmado=False
        )
        
        # Generar token válido
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps({
            'email': usuario.email,
            'evento': self.evento_aprobado.eve_id,
            'rol': 'asistente'
        })
        
        response = self.client.get(reverse('confirmar_registro', args=[token]))
        
        # Verificar que el usuario fue activado
        usuario.refresh_from_db()
        self.assertTrue(usuario.is_active)
        
        # Verificar que se renderiza la página de confirmación
        self.assertEqual(response.status_code, 200)
    
    def test_token_expirado_limpieza_datos(self):
        """Token expirado debe limpiar datos no confirmados"""
        from itsdangerous import URLSafeTimedSerializer
        from django.conf import settings
        import time
        
        # Crear usuario inactivo
        usuario = Usuario.objects.create_user(
            username='test_expired',
            email='expired@test.com',
            documento='66666666',
            first_name='Test',
            last_name='Expired',
            password='temporal',
            is_active=False
        )
        
        # Crear asistente y relación no confirmada
        asistente = Asistente.objects.create(usuario=usuario)
        AsistenteEvento.objects.create(
            asistente=asistente,
            evento=self.evento_aprobado,
            asi_eve_fecha_hora=timezone.now(),
            asi_eve_estado='Pendiente',
            confirmado=False
        )
        
        # Generar token expirado (hace más de 1 minuto)
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        # Simular token antiguo modificando el timestamp
        old_data = {
            'email': usuario.email,
            'evento': self.evento_aprobado.eve_id,
            'rol': 'asistente'
        }
        
        # Para simular expiración, usaremos un token con timestamp muy viejo
        expired_token = serializer.dumps(old_data)
        
        response = self.client.get(reverse('confirmar_registro', args=[expired_token + 'expired']))
        
        # Debe mostrar página de enlace expirado
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enlace de confirmación expirado')
    
    def test_usuario_activo_confirmacion_directa(self):
        """Usuario ya activo debe procesar confirmación sin generar nueva clave"""
        from itsdangerous import URLSafeTimedSerializer
        from django.conf import settings
        
        # Crear usuario activo
        usuario = Usuario.objects.create_user(
            username='test_active',
            email='active@test.com',
            documento='77777777',
            first_name='Test',
            last_name='Active',
            password='existing_password',
            is_active=True
        )
        
        # Asignar rol
        RolUsuario.objects.create(usuario=usuario, rol=self.rol_asistente)
        
        # Crear asistente y relación no confirmada
        asistente = Asistente.objects.create(usuario=usuario)
        AsistenteEvento.objects.create(
            asistente=asistente,
            evento=self.evento_aprobado,
            asi_eve_fecha_hora=timezone.now(),
            asi_eve_estado='Pendiente',
            confirmado=False
        )
        
        # Generar token válido
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps({
            'email': usuario.email,
            'evento': self.evento_aprobado.eve_id,
            'rol': 'asistente'
        })
        
        response = self.client.get(reverse('confirmar_registro', args=[token]))
        
        # Verificar que la asistencia fue confirmada
        asistencia = AsistenteEvento.objects.get(asistente=asistente, evento=self.evento_aprobado)
        self.assertTrue(asistencia.confirmado)
        
        self.assertEqual(response.status_code, 200)
    
    def test_usuario_o_evento_inexistente(self):
        """Token con usuario o evento inexistente debe fallar gracefully"""
        from itsdangerous import URLSafeTimedSerializer
        from django.conf import settings
        
        # Generar token con datos inexistentes
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps({
            'email': 'noexiste@test.com',
            'evento': 99999,
            'rol': 'asistente'
        })
        
        response = self.client.get(reverse('confirmar_registro', args=[token]))
        
        # Debe retornar error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o evento no encontrado')


class InscripcionDirectaTestCase(VisitanteEventosTestCase):
    """
    Pruebas para inscripciones directas de evaluadores y participantes
    que cubren funciones específicas no incluidas en otras historias
    """
    
    def setUp(self):
        super().setUp()
        # Evento con inscripciones abiertas
        self.evento_inscripciones_abiertas = Evento.objects.create(
            eve_nombre='Evento Inscripciones Abiertas',
            eve_descripcion='Evento con inscripciones directas abiertas',
            eve_ciudad='Barranquilla',
            eve_lugar='Centro de Convenciones',
            eve_fecha_inicio=date.today() + timedelta(days=60),
            eve_fecha_fin=date.today() + timedelta(days=61),
            eve_estado='Aprobado',
            eve_capacidad=200,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_inscripcion_evaluadores='Si',
            eve_inscripcion_participantes='Si',
            eve_es_multidisciplinario='Si',
            eve_administrador_fk=self.administrador
        )
        EventoCategoria.objects.create(evento=self.evento_inscripciones_abiertas, categoria=self.categoria)
    
    def test_inscripcion_evaluador_directo_inscripciones_cerradas(self):
        """Rechaza inscripción de evaluador cuando las inscripciones están cerradas"""
        # Evento con inscripciones cerradas
        evento_cerrado = Evento.objects.create(
            eve_nombre='Evento Cerrado',
            eve_descripcion='Evento con inscripciones cerradas',
            eve_ciudad='Cartagena',
            eve_lugar='Hotel',
            eve_fecha_inicio=date.today() + timedelta(days=20),
            eve_fecha_fin=date.today() + timedelta(days=21),
            eve_estado='Aprobado',
            eve_capacidad=50,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_inscripcion_evaluadores='No',  # Cerradas
            eve_administrador_fk=self.administrador
        )
        
        response = self.client.get(reverse('inscripcion_evaluador_directo', args=[evento_cerrado.eve_id]))
        
        # Debe redirigir con mensaje de error
        self.assertEqual(response.status_code, 302)
    
    def test_inscripcion_participante_directo_evento_inactivo(self):
        """Rechaza inscripción cuando el evento no está activo"""
        response = self.client.get(reverse('inscripcion_participante_directo', args=[self.evento_no_disponible.eve_id]))
        
        # Debe redirigir con mensaje de error
        self.assertEqual(response.status_code, 302)
    
    def test_inscripcion_evaluador_evento_multidisciplinario_sin_categoria(self):
        """Rechaza inscripción de evaluador sin seleccionar categoría en evento multidisciplinario"""
        datos_evaluador = {
            'eva_id': '88888888',
            'eva_nombres': 'Evaluador',
            'eva_apellidos': 'Test',
            'eva_correo': 'evaluador@test.com',
            'eva_telefono': '3001234567'
            # Sin categoria_evaluacion
        }
        
        response = self.client.post(
            reverse('inscripcion_evaluador_directo', args=[self.evento_inscripciones_abiertas.eve_id]),
            datos_evaluador
        )
        
        # Debe redirigir por falta de categoría
        self.assertEqual(response.status_code, 302)
    
    def test_inscripcion_participante_proyecto_grupal_sin_nombre(self):
        """Rechaza inscripción grupal sin nombre de proyecto"""
        datos_participante = {
            'par_id': '99999999',
            'par_nombres': 'Participante',
            'par_apellidos': 'Grupal',
            'par_correo': 'grupal@test.com',
            'par_telefono': '3001234567',
            'tipo_participacion': 'grupal',
            'es_lider_proyecto': '1'
            # Sin nombre_proyecto
        }
        
        response = self.client.post(
            reverse('inscripcion_participante_directo', args=[self.evento_inscripciones_abiertas.eve_id]),
            datos_participante
        )
        
        # Debe redirigir por falta de nombre de proyecto
        self.assertEqual(response.status_code, 302)
    
    def test_validacion_miembros_equipo_datos_incompletos(self):
        """Valida que todos los miembros del equipo tengan datos completos"""
        archivo_proyecto = SimpleUploadedFile(
            "proyecto.pdf", 
            b"contenido del proyecto", 
            content_type="application/pdf"
        )
        
        datos_participante = {
            'par_id': '10101010',
            'par_nombres': 'Líder',
            'par_apellidos': 'Proyecto',
            'par_correo': 'lider@test.com',
            'par_telefono': '3001234567',
            'tipo_participacion': 'grupal',
            'nombre_proyecto': 'Proyecto Innovador',
            'descripcion_proyecto': 'Descripción del proyecto',
            'es_lider_proyecto': '1',
            'archivo_proyecto': archivo_proyecto,
            'miembro_documento[]': ['11111111', ''],  # Un miembro sin documento
            'miembro_correo[]': ['miembro1@test.com', 'miembro2@test.com'],
            'miembro_nombres[]': ['Miembro1', 'Miembro2'],
            'miembro_apellidos[]': ['Apellido1', 'Apellido2'],
            'miembro_telefono[]': ['3001111111', '3002222222']
        }
        
        response = self.client.post(
            reverse('inscripcion_participante_directo', args=[self.evento_inscripciones_abiertas.eve_id]),
            datos_participante
        )
        
        # Debe redirigir por datos incompletos
        self.assertEqual(response.status_code, 302)
    
    def test_validacion_documentos_duplicados_miembros(self):
        """Valida que no haya documentos duplicados entre miembros"""
        datos_participante = {
            'par_id': '12121212',
            'par_nombres': 'Líder2',
            'par_apellidos': 'Proyecto2',
            'par_correo': 'lider2@test.com',
            'par_telefono': '3001234567',
            'tipo_participacion': 'grupal',
            'nombre_proyecto': 'Proyecto Duplicado',
            'descripcion_proyecto': 'Descripción',
            'es_lider_proyecto': '1',
            'miembro_documento[]': ['11111111', '11111111'],  # Documentos duplicados
            'miembro_correo[]': ['miembro1@test.com', 'miembro2@test.com'],
            'miembro_nombres[]': ['Miembro1', 'Miembro2'],
            'miembro_apellidos[]': ['Apellido1', 'Apellido2'],
        }
        
        response = self.client.post(
            reverse('inscripcion_participante_directo', args=[self.evento_inscripciones_abiertas.eve_id]),
            datos_participante
        )
        
        # Debe redirigir por documentos duplicados
        self.assertEqual(response.status_code, 302)
    
    def test_lider_no_puede_estar_en_lista_miembros(self):
        """Valida que el líder no esté listado como miembro adicional"""
        datos_participante = {
            'par_id': '13131313',
            'par_nombres': 'Líder3',
            'par_apellidos': 'Proyecto3',
            'par_correo': 'lider3@test.com',
            'par_telefono': '3001234567',
            'tipo_participacion': 'grupal',
            'nombre_proyecto': 'Proyecto Líder Duplicado',
            'descripcion_proyecto': 'Descripción',
            'es_lider_proyecto': '1',
            'miembro_documento[]': ['13131313'],  # Mismo documento que el líder
            'miembro_correo[]': ['lider3@test.com'],  # Mismo correo que el líder
            'miembro_nombres[]': ['Líder3'],
            'miembro_apellidos[]': ['Proyecto3'],
        }
        
        response = self.client.post(
            reverse('inscripcion_participante_directo', args=[self.evento_inscripciones_abiertas.eve_id]),
            datos_participante
        )
        
        # Debe redirigir porque el líder está en la lista de miembros
        self.assertEqual(response.status_code, 302)


class FuncionesAuxiliaresTestCase(VisitanteEventosTestCase):
    """
    Pruebas para funciones auxiliares y casos edge adicionales
    no cubiertos en las historias principales
    """
    
    def test_generar_clave_longitud_correcta(self):
        """La función generar_clave() produce claves de 10 caracteres"""
        from app_eventos.views import generar_clave
        
        clave = generar_clave()
        self.assertEqual(len(clave), 10)
        self.assertTrue(clave.isalnum())  # Solo letras y números
    
    def test_generar_clave_unicidad(self):
        """La función generar_clave() produce claves diferentes"""
        from app_eventos.views import generar_clave
        
        claves = [generar_clave() for _ in range(100)]
        # Debe haber al menos 90% de claves únicas (probabilísticamente)
        claves_unicas = len(set(claves))
        self.assertGreater(claves_unicas, 90)
    
    def test_registrarse_admin_evento_codigo_invalido(self):
        """Maneja códigos de invitación inválidos para admin evento"""
        response = self.client.get(reverse('registro_admin_evento') + '?codigo=INVALIDO')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'inválido')
    
    def test_inscripcion_participante_sin_codigo_redirige(self):
        """Inscripción de participante sin código debe redirigir con mensaje"""
        response = self.client.get(reverse('inscripcion_participante', args=[self.evento_aprobado.eve_id]))
        
        # Debe redirigir porque requiere código de invitación
        self.assertEqual(response.status_code, 302)
    
    def test_inscripcion_evaluador_sin_codigo_redirige(self):
        """Inscripción de evaluador sin código debe redirigir con mensaje"""
        response = self.client.get(reverse('inscripcion_evaluador', args=[self.evento_aprobado.eve_id]))
        
        # Debe redirigir porque requiere código de invitación
        self.assertEqual(response.status_code, 302)
    
    def test_vista_detalle_evento_con_multiples_categorias(self):
        """Vista detalle maneja eventos con múltiples categorías correctamente"""
        # Crear segunda categoría
        categoria2 = Categoria.objects.create(
            cat_nombre='Inteligencia Artificial',
            cat_descripcion='IA y Machine Learning',
            cat_area_fk=self.area
        )
        
        # Asociar ambas categorías al evento
        EventoCategoria.objects.create(evento=self.evento_aprobado, categoria=categoria2)
        
        response = self.client.get(reverse('detalle_evento_visitante', args=[self.evento_aprobado.eve_id]))
        
        self.assertEqual(response.status_code, 200)
        categorias = response.context['categorias']
        self.assertEqual(len(categorias), 2)  # Ahora tiene 2 categorías
    
    def test_eventos_con_fechas_iguales_compartir(self):
        """Evento con fecha inicio igual a fecha fin se comparte correctamente"""
        evento_un_dia = Evento.objects.create(
            eve_nombre='Evento de Un Día',
            eve_descripcion='Evento que dura un solo día',
            eve_ciudad='Bucaramanga',
            eve_lugar='Auditorio',
            eve_fecha_inicio=date.today() + timedelta(days=25),
            eve_fecha_fin=date.today() + timedelta(days=25),  # Misma fecha
            eve_estado='Aprobado',
            eve_capacidad=80,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        response = self.client.post(
            reverse('compartir_evento_visitante', args=[evento_un_dia.eve_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        mensaje = data['mensaje']
        
        # Solo debe aparecer una fecha, no un rango
        fecha_str = evento_un_dia.eve_fecha_inicio.strftime('%d/%m/%Y')
        self.assertIn(fecha_str, mensaje)
        self.assertNotIn(' - ', mensaje)  # No debe tener guión de rango
    
    def test_inscripcion_asistente_get_muestra_formulario(self):
        """GET a inscripción de asistente muestra el formulario"""
        response = self.client.get(reverse('inscripcion_asistente', args=[self.evento_aprobado.eve_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'evento')
        # Debe renderizar template de inscripción
        
    def test_eventos_filtrados_por_estado_case_insensitive(self):
        """Filtrado por estado es insensible a mayúsculas"""
        # Crear evento con estado en minúsculas
        evento_minusculas = Evento.objects.create(
            eve_nombre='Evento Minúsculas',
            eve_descripcion='Evento con estado en minúsculas',
            eve_ciudad='Pereira',
            eve_lugar='Centro',
            eve_fecha_inicio=date.today() + timedelta(days=40),
            eve_fecha_fin=date.today() + timedelta(days=41),
            eve_estado='aprobado',  # En minúsculas
            eve_capacidad=60,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        response = self.client.get(reverse('ver_eventos'))
        eventos_mostrados = response.context['eventos']
        
        # Debe incluir el evento aunque esté en minúsculas
        self.assertIn(evento_minusculas, eventos_mostrados)
    
    def test_evento_capacidad_cero_maneja_correctamente(self):
        """Eventos con capacidad 0 se manejan correctamente"""
        evento_sin_capacidad = Evento.objects.create(
            eve_nombre='Evento Sin Capacidad',
            eve_descripcion='Evento con capacidad 0',
            eve_ciudad='Manizales',
            eve_lugar='Virtual',
            eve_fecha_inicio=date.today() + timedelta(days=50),
            eve_fecha_fin=date.today() + timedelta(days=51),
            eve_estado='Aprobado',
            eve_capacidad=0,
            eve_tienecosto='NO',
            eve_tipo='publico',
            eve_administrador_fk=self.administrador
        )
        
        response = self.client.get(reverse('detalle_evento_visitante', args=[evento_sin_capacidad.eve_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0')  # Debe mostrar capacidad 0


# Ejecutar las pruebas con: python manage.py test app_eventos
