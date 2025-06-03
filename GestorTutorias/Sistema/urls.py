
from django.urls import  path

from .views import IndexView, CrearUsuarioView, inicioSesion,CordinadorDashboard , CerrarSesionView ,verUsuarios


urlpatterns = [
    
    path('', IndexView.as_view(), name='index'),
    path('crear_usuario', CrearUsuarioView.as_view(), name='crear_usuario'),
    path('inicioSesion', inicioSesion.as_view(), name='inciarSesion'),
    path('cordinadorDashboard', CordinadorDashboard.as_view(), name='cordinadorDashboard'),
     path('cerrar_sesion/',  CerrarSesionView.as_view(), name='cerrar_sesion'),
    path('ver_usuarios/', verUsuarios.as_view(), name='ver_usuarios'),
]