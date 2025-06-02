from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


from .models import usuario, tutor, alumno, cordinador, horario, solicitud, Feedback
from .forms import CrearUsusuarioForm, EliminarUsuarioForm, EditarUsuarioForm
# Create your views here.
class IndexView:
    def get(self, request):
        return render(request, 'index.html')
    
class inicioSesion(LoginView):
    template_name = 'login.html'  # tu plantilla de inicio de sesión
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')  # reemplaza 'home' por tu vista destino

    def get_success_url(self):
        return self.success_url