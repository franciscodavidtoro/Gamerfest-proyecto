
from django.urls import  path

from .views import IndexView, CrearUsuarioView

urlpatterns = [
    
    path('', IndexView.as_view(), name='index'),
    path('crear_usuario', CrearUsuarioView.as_view(), name='crear_usuario'),
]