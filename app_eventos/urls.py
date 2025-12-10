from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('', views.ver_eventos, name='ver_eventos'),
    path('detalle-evento/<int:eve_id>/', views.detalle_evento, name='detalle_evento_visitante'),
    path('<int:eve_id>/compartir/', views.compartir_evento_visitante, name='compartir_evento_visitante'),
    path('inscripcion-asistente/<int:eve_id>/', views.inscripcion_asistente, name='inscripcion_asistente'),
    path('registro-con-codigo/<str:codigo>/', views.registro_con_codigo, name='registro_con_codigo'),
    path('inscripcion-evaluador-directo/<int:eve_id>/', views.inscripcion_evaluador_directo, name='inscripcion_evaluador_directo'),
    path('inscripcion-participante-directo/<int:eve_id>/', views.inscripcion_participante_directo, name='inscripcion_participante_directo'),
    path('confirmar-inscripcion-directa/<str:token>/', views.confirmar_inscripcion_directa, name='confirmar_inscripcion_directa'),
    path('logout/', LogoutView.as_view(next_page='ver_eventos'), name='logout'),
    path('confirmar-registro/<str:token>/', views.confirmar_registro, name='confirmar_registro'),
    path('registro_admin_evento/', views.registrarse_admin_evento, name='registro_admin_evento'),

]