from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout


from datetime import datetime, timedelta


from .models import usuario, tutor, alumno, cordinador, horario, solicitud, Feedback
from .forms import CrearUsusuarioForm, EliminarUsuarioForm, EditarUsuarioForm, CambiarContrasennaForm, CrearHorarioForm, CrearSolicitudForm, crearFeedbackForm
# Create your views here.
class IndexView(View):
    def get(self, request):
        #si no ay usuarios redirije a crear usuario 
        if not usuario.objects.exists():
            return redirect('crear_usuario')
        
        return render(request, 'index.html')
    
class inicioSesion(LoginView):
    template_name = 'login.html'  # tu plantilla de inicio de sesión
    redirect_authenticated_user = True
    

    def get_success_url(self):
        if cordinador.objects.filter(usuario=self.request.user).exists():
            return reverse_lazy('cordinadorDashboard')
        elif tutor.objects.filter(usuario=self.request.user).exists():
            return reverse_lazy('ver_horario')
        elif alumno.objects.filter(usuario=self.request.user).exists():
            return reverse_lazy('crear_solicitud')
        else:
            return reverse_lazy('home')
        
    
class CrearUsuarioView(View):
    template_name='crear_usuario.html'
    form_class = CrearUsusuarioForm
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            if request.user.is_authenticated:
                return redirect('CordinadorDashboard')
            return  redirect('inciarSesion') 
        return render(request, self.template_name, {'form': form, 'error': 'Error al crear el usuario'})
    
class EditarUsuarioView(View):
    template_name='editar_usuario.html'
    form_class = EditarUsuarioForm
    success_url = reverse_lazy('') #corejir
    
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
    success_url = reverse_lazy('') #corejir
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

class crearFeedback(View):
    template_name = 'crear_feedback.html'
    form_class = crearFeedbackForm
    
    def get(self, request, solicitud_id):
        try:
            solicitud_instance = solicitud.objects.get(id=solicitud_id)
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")
        
        
        if hasattr(request.user, 'alumno') and solicitud_instance.estudiante == request.user.alumno:
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
        else:
            return HttpResponse("No tienes permiso para crear un feedback")
    
    def post(self, request, solicitud_id):
        try:
            solicitud_instance = solicitud.objects.get(id=solicitud_id)
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")
        

        
        if hasattr(request.user, 'alumno')  and solicitud_instance.estudiante == request.user.alumno:
            form = self.form_class(request.POST)
            if form.is_valid() :
                feedback_instance = form.save(commit=False)
                feedback_instance.cordinador = request.user.cordinador
                feedback_instance.save()
                return HttpResponse("Feedback creado correctamente")
            else:
                return render(request, self.template_name, {'form': form, 'error': 'Error al crear el feedback'})
        else:
            return HttpResponse("No tienes permiso para crear un feedback")
        


def obtener_horarios_Semana(dia, profesor):
    """
    Obtiene los horarios de una semana para un profesor específico.
    
    Args:
        dia (str): Día de la semana en formato 'YYYY-MM-DD'.
        profesor (tutor): Instancia del tutor para el cual se obtienen los horarios.
        
    Returns:
        list: Lista de horarios disponibles para el profesor en esa semana.
    """
    
    
    fecha_inicio = datetime.strptime(dia, '%Y-%m-%d')
    horarios = []
    
    for i in range(7):
        fecha_actual = fecha_inicio + timedelta(days=i)
        horarios_dia = horario.objects.filter(tutor=profesor, fecha=fecha_actual, disponibilidad=True)
        horarios.extend(horarios_dia)
    
    return horarios

def exixten_horarios(dia, profesor):
    """
    Verifica si existen horarios para un profesor en un día y para adelante.
    
    Args:
        dia (str): Día de la semana en formato 'YYYY-MM-DD'.
        profesor (tutor): Instancia del tutor para el cual se verifica la existencia de horarios.
        
    Returns:
        bool: True si existen horarios, False en caso contrario.
    """
    
    
    fecha = datetime.strptime(dia, '%Y-%m-%d')
    return horario.objects.filter(tutor=profesor, fecha__gte=fecha, disponibilidad=True).exists()







class verHorario(View):
    template_name = 'ver_horario.html'
    
    def get(self, request, dia):
        if hasattr(request.user, 'tutor'):
            horarios = obtener_horarios_Semana(dia, request.user.tutor)
            diaSiguienteSemana = (datetime.strptime(dia, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
            extHoratios = exixten_horarios(diaSiguienteSemana, request.user.tutor)
        else:
            horarios = []
        
        return render(request, self.template_name, {'horarios': horarios, 'extHoratios': extHoratios})
    
    
    
    
    
    
    
    
    
    
    
class CordinadorDashboard(View):
    template_name = 'cordinador_dashboard.html'
    
    def get(self, request):
        if self.request.user.coordinador:
            
            return render(request, self.template_name)
        else:
            return HttpResponse("No tienes permiso para acceder a este dashboard")

        
        
        
        
class CerrarSesionView(View):
    def get(self, request):
        logout(request)
        return redirect('inciarSesion')
    
    
    
class verUsuarios(View):
    template_name = 'ver_usuarios.html'
    
    def get(self, request):
        usuarios = usuario.objects.all()
        return render(request, self.template_name, {'usuarios': usuarios})