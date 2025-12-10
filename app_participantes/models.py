from django.db import models
from app_eventos.models import Evento
from app_usuarios.models import Usuario
from app_areas.models import Categoria

class Participante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='participante')

    def __str__(self):
        return f"{self.usuario.username}"


class ProyectoGrupal(models.Model):
    """Modelo para manejar proyectos grupales en eventos"""
    nombre_proyecto = models.CharField(max_length=200)
    descripcion_proyecto = models.TextField(blank=True, null=True)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    archivo_proyecto = models.FileField(upload_to='proyectos/archivos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=45, default='Pendiente')
    
    # Categoría(s) del proyecto para eventos multidisciplinarios
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='proyectos_grupales',
                                        help_text="Categoría(s) en las que participa el proyecto")
    # Nota del proyecto (se aplica a todos los integrantes)
    nota_proyecto = models.FloatField(null=True, blank=True, 
                                      help_text="Nota del proyecto que se aplica a todos los integrantes")
    
    def __str__(self):
        return f"{self.nombre_proyecto} - {self.evento.eve_nombre}"
    
    def obtener_integrantes(self):
        """Retorna todos los participantes del proyecto"""
        return ParticipanteEvento.objects.filter(proyecto_grupal=self).select_related('participante__usuario')


class ParticipanteEvento(models.Model):
    """Relación entre Participante y Evento - puede ser individual o grupal"""
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    par_eve_fecha_hora = models.DateTimeField()
    par_eve_documentos = models.FileField(upload_to='participantes/documentos/', null=True, blank=True)
    par_eve_estado = models.CharField(max_length=45)
    par_eve_qr = models.ImageField(upload_to='participantes/qr/', null=True, blank=True)
    par_eve_valor = models.FloatField(null=True, blank=True)
    confirmado = models.BooleanField(default=False)
    
    # Campos para proyectos grupales
    es_grupal = models.BooleanField(default=False)
    proyecto_grupal = models.ForeignKey(ProyectoGrupal, on_delete=models.CASCADE, null=True, blank=True)
    es_lider_proyecto = models.BooleanField(default=False)  # Solo uno por proyecto
    
    # Categoría(s) para participaciones individuales en eventos multidisciplinarios
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='participantes_evento',
                                        help_text="Categoría(s) en las que participa (solo para inscripciones individuales)")

    class Meta:
        unique_together = (('participante', 'evento'),)
