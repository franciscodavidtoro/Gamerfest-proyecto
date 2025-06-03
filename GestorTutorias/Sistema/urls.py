
from django.urls import  path

from .views import IndexView, CrearUsuarioView, inicioSesion,CordinadorDashboard

urlpatterns = [
    
    path('', IndexView.as_view(), name='index'),
    path('crear_usuario', CrearUsuarioView.as_view(), name='crear_usuario'),
    path('inicioSesion', inicioSesion.as_view(), name='inciarSesion'),
    path('cordinadorDashboard', CordinadorDashboard.as_view(), name='cordinadorDashboard'),
]