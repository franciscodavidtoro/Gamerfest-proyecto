from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.db.models import Avg

from datetime import datetime, timedelta,date


from .models import usuario, tutor, alumno, cordinador, horario, solicitud, Feedback
from .forms import CrearUsusuarioForm, EditarUsuarioForm, CambiarContrasennaForm, CrearHorarioForm, CrearSolicitudForm, crearFeedbackForm
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
        if usuario.objects.filter(username=self.request.user.username, Eliminado=True).exists():
            return reverse_lazy('cerrar_sesion')
        
        if cordinador.objects.filter(usuario=self.request.user).exists():
            return reverse_lazy('cordinadorDashboard')
        elif tutor.objects.filter(usuario=self.request.user).exists():
            return reverse_lazy('PagTutor')
        elif alumno.objects.filter(usuario=self.request.user).exists():
            return reverse_lazy('PagEstudiante')
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
                return redirect('cordinadorDashboard')
            return  redirect('inciarSesion') 
        return render(request, self.template_name, {'form': form, 'error': 'Error al crear el usuario'})
    
class EditarUsuarioView(View):
    template_name='editar_usuario.html'
    form_class = EditarUsuarioForm
    
    
    def get(self, request,pk):
        form = self.form_class(instance=usuario.objects.get(id=pk))
        return render(request, self.template_name, {'form': form})
    
    def post(self, request,pk):
        form = self.form_class(request.POST, instance=usuario.objects.get(id=pk))
        if form.is_valid():
            form.save()
            return redirect('ver_usuarios')
        
class EliminarUsuarioView(View):
    def get(self, request,pk):
        return render(request, 'eliminar_usuario.html')
    def post(self, request,pk):
        user = get_object_or_404(usuario, pk=pk)
        user.Eliminado = True
        user.save()
        return redirect('ver_usuarios') 
        
            
            
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
                                      hora_inicio=horario_instance.hora_inicio
                                      ).exists():
                return render(request, self.template_name, {'form': form, 'error': 'El horario ya existe o interfiere con otro horario'})
  
            form.save()
            return redirect('PagTutor') 
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Error al crear el horario'})
        


    
class crearSolicitud(View):
    template_name = 'crear_solicitud.html'
    form_class = CrearSolicitudForm  
    def get(self, request,pk):
        if hasattr(request.user, 'alumno'):
            form = self.form_class()
            horarios = horario.objects.filter(disponibilidad=True)
            return render(request, self.template_name, {'form': form, 'horarios': horarios})
        else:
            return HttpResponse("No tienes permiso para crear una solicitud")
    def post(self, request,pk):
        if hasattr(request.user, 'alumno'):
            form = self.form_class(request.POST)
            if form.is_valid():
                solicitud_instance = form.save(commit=False)
                solicitud_instance.estudiante = request.user.alumno
                solicitud_instance.horario = get_object_or_404(horario, id=pk)
                solicitud_instance.save()
                return redirect('PagEstudiante')
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
    def get(self, request, pk):
        try:
            solicitud_instance = solicitud.objects.get(id=pk)

            # Cambiar disponibilidad en el horario relacionado
            solicitud_instance.horario.disponibilidad = False
            solicitud_instance.horario.save()

            # Cambiar el estado de la solicitud y guardar
            solicitud_instance.estado = 'Aceptada'
            solicitud_instance.save()

            return redirect('Tutorias_pendientes')

        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")


class rechazarSolicitud(View):
    def get(self, request, pk):
        try:
            solicitud_instance = solicitud.objects.get(id=pk)
            
            solicitud_instance.estado = 'Rechazada'
            solicitud_instance.save()
            return redirect('Tutorias_pendientes')
            
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")

class crearFeedback(View):
    template_name = 'crear_feedback.html'
    form_class = crearFeedbackForm
    
    def get(self, request, pk):
        try:
            solicitud_instance = solicitud.objects.get(id=pk)
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")
        
        
        if hasattr(request.user, 'alumno') and solicitud_instance.estudiante == request.user.alumno:
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
        else:
            return HttpResponse("No tienes permiso para crear un feedback")
    
    def post(self, request, pk):
        try:
            solicitud_instance = solicitud.objects.get(id=pk)
        except solicitud.DoesNotExist:
            return HttpResponse("Solicitud no encontrada")
        

        form = self.form_class(request.POST)
        if form.is_valid() :
            feedback_instance = form.save(commit=False)
            feedback_instance.solicitud = solicitud_instance
            feedback_instance.save()
            return redirect('PagEstudiante')
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Error al crear el feedback'})
        
        
        


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


def horariosPendiente(dia, profesor):
    #obtine todos los horarios aprovados para el profesor
    fecha_inicio = datetime.strptime(dia, '%Y-%m-%d')
    horarios = horario.objects.filter(tutor=profesor, fecha__gte=fecha_inicio)
    if not horarios:
        return []

    return horarios





class PagTutor(View):
    template_name = 'PagTutor.html'
    
    def get(self, request, dia=None):
        if not dia:
            dia = datetime.today().strftime('%Y-%m-%d')
        
        horarios = obtener_horarios_Semana(dia, request.user.tutor)
        diaSiguienteSemana = (datetime.strptime(dia, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
        extHoratios = exixten_horarios(diaSiguienteSemana, request.user.tutor)
        fechaHoy =date.today().strftime('%Y-%m-%d')
        horariosPendientes = horariosPendiente(fechaHoy, request.user.tutor)
        
        
        return render(request, self.template_name, {'horarios': horarios, 'extHoratios': extHoratios, 'horariosPendientes': horariosPendientes, 'dia': dia})
    
    
class PagEstudiante(View):
    template_name = 'PagEstudiante.html'
    def get(self, request):
        fecha_inicio =datetime.today().strftime('%Y-%m-%d')
        
        solicitudes = solicitud.objects.filter(estudiante=request.user.alumno, estado='Aceptada')
        horarios_ids = solicitudes.values_list('horario_id', flat=True)

        horariosPendientes = horario.objects.filter(
            fecha__gte=fecha_inicio,
            disponibilidad=False,
            id__in=horarios_ids
        )
        solicitudes_sin_feedback = solicitud.objects.filter(estudiante=request.user.alumno, estado='Aceptada').exclude(feedbacks__isnull=False)

        
        return render(request, self.template_name, {'solicitudes':solicitudes_sin_feedback, 'horarios': horariosPendientes})
        
        
        
class elegirProfesor(View):
    template_name = 'elegir_profesor.html'
    def get(self, request):
        profesores = usuario.objects.filter(tutor__isnull=False, Eliminado=False)
        return render(request, self.template_name, {'profesores': profesores})
    
class ver_horarios_profesor(View):
    template_name = 'ver_horarios_profesor.html'
    def get(self, request, pk):
        profesor = get_object_or_404(tutor, usuario__id=pk)
        horarios = horario.objects.filter(tutor=profesor, disponibilidad=True)
        return render(request, self.template_name, { 'horarios': horarios})
    
    
    
    
    
    
    
    
    
    
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
        usuarios = usuario.objects.filter(Eliminado=False)
        return render(request, self.template_name, {'usuarios': usuarios})
    
    
    
class Tutorias_pendientes(View):
    template_name = 'tutorias_pendientes.html'
    
    def get(self, request):
        
        solicitudes = solicitud.objects.filter(estado='pendiente')
        return render(request, self.template_name, {'solicitudes': solicitudes})
        
        
        
        
class Estadisticas(View):
    template_name = 'estadisticas.html'
    
    def get(self, request):
        
            usuarios = usuario.objects.filter(Eliminado=False).count()
            tutores = tutor.objects.all().exclude(usuario__Eliminado=True).count()
            alumnos = alumno.objects.all().exclude(usuario__Eliminado=True).count()
            coordinadores = cordinador.objects.all().exclude(usuario__Eliminado=True).count()
            
            
        
            PromedioFeedbacksTutores = Feedback.objects.filter(solicitud__horario__tutor__usuario__Eliminado=False)\
                                        .values('solicitud__horario__tutor__usuario__username')\
                                        .annotate(promedio=Avg('calificacion'))\
                                        .order_by('-promedio')
                                        
            
            
            return render(request, self.template_name, {
                'usuarios': usuarios,
                'tutores': tutores,
                'alumnos': alumnos,
                'coordinadores': coordinadores,
                'PromedioFeedbacksTutores': PromedioFeedbacksTutores
            })
       
            