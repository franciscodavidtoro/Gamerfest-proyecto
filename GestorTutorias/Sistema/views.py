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
    
class CrearUsuarioView(View):
    template_name='crear_usuario.html'
    form_class = CrearUsusuarioForm
    success_url = reverse_lazy('home')
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Usuario creado correctamente")
    
class EditarUsuarioView(View):
    template_name='editar_usuario.html'
    form_class = EditarUsuarioForm
    success_url = reverse_lazy('home')
    
    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse("Usuario editado correctamente")
        
class EliminarUsuarioView(View):
    template_name='eliminar_usuario.html'
    form_class = EliminarUsuarioForm
    success_url = reverse_lazy('home')  
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = usuario.objects.get(username=username)
                user.delete()
                return HttpResponse("Usuario eliminado correctamente")
            except usuario.DoesNotExist:
                return HttpResponse("El usuario no existe")
            
            
class cambiarContrasenna(View):
    template_name = 'cambiar_contrasenna.html'
    form_class = CambiarContrasennaForm
    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = self.form_class(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse("Contraseña cambiada correctamente")
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Error al cambiar la contraseña'})
        
class crearHorario(View):
    template_name = 'crear_horario.html'
    form_class = CrearHorarioForm
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            horario_instance = form.save(commit=False)
            horario_instance.tutor = request.user.tutor
            #verificar si el horario ya existe 
            if horario.objects.filter(tutor=horario_instance.tutor, fecha=horario_instance.fecha,
                                      hora_inicio=horario_instance.hora_fin
                                      ).exists():
                return render(request, self.template_name, {'form': form, 'error': 'El horario ya existe o interfiere con otro horario'})
            
            
            form.save()
            return HttpResponse("Horario creado correctamente")
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Error al crear el horario'})
        

class verHorario(View):
    template_name = 'ver_horario.html'
    
    def get(self, request):
        if hasattr(request.user, 'tutor'):
            horarios = horario.objects.filter(tutor=request.user.tutor)
        else:
            horarios = []
        
        return render(request, self.template_name, {'horarios': horarios})
    
class crearSolicitud(View):
    template_name = 'crear_solicitud.html'
    form_class = CrearSolicitudForm  
    def get(self, request):
        if hasattr(request.user, 'alumno'):
            form = self.form_class()
            horarios = horario.objects.filter(disponibilidad=True)
            return render(request, self.template_name, {'form': form, 'horarios': horarios})
        else:
            return HttpResponse("No tienes permiso para crear una solicitud")
    def post(self, request):
        if hasattr(request.user, 'alumno'):
            form = self.form_class(request.POST)
            if form.is_valid():
                solicitud_instance = form.save(commit=False)
                solicitud_instance.estudiante = request.user.alumno
                solicitud_instance.save()
                return HttpResponse("Solicitud creada correctamente")
            else:
                return render(request, self.template_name, {'form': form, 'error': 'Error al crear la solicitud'})
        else:
            return HttpResponse("No tienes permiso para crear una solicitud")
    
    
class verSolicitudes(View):
    template_name = 'ver_solicitudes.html'
    def get(self, request):
        if hasattr(request.user, 'tutor'):
            solicitudes = solicitud.objects.filter(horario__tutor=request.user.tutor)
        elif hasattr(request.user, 'alumno'):
            solicitudes = solicitud.objects.filter(estudiante=request.user.alumno)
        elif hasattr(request.user, 'cordinador'):
            solicitudes = solicitud.objects.all()
            return render(request, self.template_name, {'solicitudes': solicitudes, 'cordinador': True})
        
        return render(request, self.template_name, {'solicitudes': solicitudes})
    
class aceptarSolicitud(View):
    def get(self,request, solicitud_id):
        try:
            solicitud_instance = solicitud.objects.get(id=solicitud_id)
            if hasattr(request.user, 'cordinador') :
                solicitud_instance.horario.disponibilidad = False
                solicitud_instance.horario.save()
                solicitud_instance.estado = 'Aceptada'
                return HttpResponse("Solicitud aceptada correctamente")
            else:
                return HttpResponse("No tienes permiso para aceptar esta solicitud")
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")

class rechazarSolicitud(View):
    def get(self, request, solicitud_id):
        try:
            solicitud_instance = solicitud.objects.get(id=solicitud_id)
            if hasattr(request.user, 'cordinador'):
                solicitud_instance.estado = 'Rechazada'
                solicitud_instance.save()
                return HttpResponse("Solicitud rechazada correctamente")
            else:
                return HttpResponse("No tienes permiso para rechazar esta solicitud")
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")


        

        