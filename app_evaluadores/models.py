from django.db import models
from app_eventos.models import Evento
from app_participantes.models import Participante
from app_usuarios.models import Usuario
from app_areas.models import Categoria

class Evaluador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='evaluador')

    def __str__(self):
        return f"{self.usuario.username}"


class EvaluadorEvento(models.Model):
    """Relación entre Evaluador y Evento - ahora con categoría específica para eventos multidisciplinarios"""
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    eva_eve_documentos = models.FileField(upload_to='evaluadores/documentos/', null=True, blank=True)
    eva_eve_fecha_hora = models.DateTimeField()
    eva_eve_estado = models.CharField(max_length=45)
    eva_eve_qr = models.ImageField(upload_to='evaluadores/qr/', null=True, blank=True)
    confirmado = models.BooleanField(default=False)
    
    # Campo para eventos multidisciplinarios
    categoria_evaluacion = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, 
                                           help_text="Categoría específica que evalúa en eventos multidisciplinarios")

    class Meta:
        unique_together = (('evaluador', 'evento'),)

    def __str__(self):
        categoria_info = f" - {self.categoria_evaluacion.cat_nombre}" if self.categoria_evaluacion else ""
        return f"{self.evaluador.usuario.first_name} {self.evaluador.usuario.last_name} - {self.evento.eve_nombre}{categoria_info}"
    

class Criterio(models.Model):
    cri_id = models.AutoField(primary_key=True)
    cri_descripcion = models.CharField(max_length=100)
    cri_peso = models.FloatField()
    cri_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='criterios')

class Calificacion(models.Model):
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    criterio = models.ForeignKey(Criterio, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    cal_valor = models.IntegerField()
    cal_observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('evaluador', 'criterio', 'participante'),)
