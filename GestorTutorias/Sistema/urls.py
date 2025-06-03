
from django.urls import  path

from .views import IndexView, CrearUsuarioView, inicioSesion,CordinadorDashboard , CerrarSesionView ,verUsuarios, EliminarUsuarioView, EditarUsuarioView
from .views import PagTutor, crearHorario,PagEstudiante

urlpatterns = [
    
    path('', IndexView.as_view(), name='index'),
    path('crear_usuario', CrearUsuarioView.as_view(), name='crear_usuario'),
    path('inicioSesion', inicioSesion.as_view(), name='inciarSesion'),
    path('cordinadorDashboard', CordinadorDashboard.as_view(), name='cordinadorDashboard'),
     path('cerrar_sesion/',  CerrarSesionView.as_view(), name='cerrar_sesion'),
    path('ver_usuarios/', verUsuarios.as_view(), name='ver_usuarios'),
    path('eliminar_usuario/<int:pk>/', EliminarUsuarioView.as_view(), name='eliminar_usuario'),
    path('editar_usuario/<int:pk>/', EditarUsuarioView.as_view(), name='editar_usuario'),
    path('tutor/<str:pk>/', PagTutor.as_view(), name='PagTutorParametro'),
    path('tutor/', PagTutor.as_view(), name='PagTutor'),
    path('crearHorario', crearHorario.as_view(), name='crearHorario'),
    path('PagEstudiante', PagEstudiante.as_view(), name='PagEstudiante'),
]