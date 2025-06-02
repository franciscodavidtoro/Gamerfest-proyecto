from django.db import models

from django.contrib.auth.models import AbstractUser
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator, MaxValueValidator


class usuario(AbstractUser):
    # Extend the default user model with additional fields if necessary
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    def __str__(self):
        return self.username

class tutor(models.Model):
    usuario = models.OneToOneField(usuario, on_delete=models.CASCADE, related_name='tutor')

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'
        

class alumno(models.Model):
    usuario = models.OneToOneField(usuario, on_delete=models.CASCADE, related_name='alumno')

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return self.usuario.username
    
class cordinador(models.Model):
    usuario = models.OneToOneField(usuario, on_delete=models.CASCADE, related_name='coordinador')

    class Meta:
        verbose_name = 'Coordinador'
        verbose_name_plural = 'Coordinadores'

    def __str__(self):
        return self.usuario.username


class horario(models.Model):
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tutor = models.ForeignKey(tutor, on_delete=models.CASCADE, related_name='horarios')
    disponibilidad = models.BooleanField(default=True)
    

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'

    def __str__(self):
        return f"{self.hora_inicio} - {self.hora_fin} || {self.tutor.usuario.username} || {self.fecha}"

class solicitud(models.Model):
    estudiante = models.ForeignKey(alumno, on_delete=models.CASCADE, related_name='solicitudes')
    horario = models.ForeignKey(horario, on_delete=models.CASCADE, related_name='solicitudes')
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente')
    motivo= models.TextField(blank=True, null=True)
    
class Feedback(models.Model):
    solicitud = models.ForeignKey(solicitud, on_delete=models.CASCADE, related_name='feedbacks')
    comentario = models.TextField()
    calificacion = models.IntegerField(default=0,validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ] )
    

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"Feedback for {self.solicitud.estudiante.usuario.username} - {self.calificacion}"
    



auditlog.register(usuario)
auditlog.register(tutor)
auditlog.register(alumno)
auditlog.register(cordinador)
auditlog.register(horario)
auditlog.register(solicitud)
auditlog.register(Feedback)