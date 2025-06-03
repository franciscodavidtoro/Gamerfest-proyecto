from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm ,SetPasswordForm
from .models import usuario, tutor, alumno, cordinador, horario, solicitud,Feedback


class CrearUsusuarioForm(UserCreationForm):
    Roles = (
        ('1', 'Tutor'),
        ('2', 'Alumno'),
        ('3', 'Coordinador'),
    )
    rol = forms.ChoiceField(choices=Roles, label='Rol', required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = usuario
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name' )
        
    def save(self, commit=True):
        NuevoUsuario = super().save(commit=commit)
        NuevoUsuario.is_active = True
        NuevoUsuario.save()  
        
        rolSelecionado = self.cleaned_data['rol']
        
        if rolSelecionado == '1':
            tutor.objects.create(usuario=NuevoUsuario)
        elif rolSelecionado == '2':
            alumno.objects.create(usuario=NuevoUsuario)
        elif rolSelecionado == '3':
            cordinador.objects.create(usuario=NuevoUsuario)
        
        return NuevoUsuario 
    
    

    
class EditarUsuarioForm(UserChangeForm):
    
    Roles = (
        ('1', 'Tutor'),
        ('2', 'Alumno'),
        ('3', 'Coordinador'),
    )
    rol = forms.ChoiceField(choices=Roles, label='Rol', required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = usuario
        fields = ('username', 'email', 'first_name', 'last_name')
        
    def save(self, commit=True):
        NuevoUsuario = super().save(commit=commit)
        
        rolSelecionado = self.cleaned_data['rol']
        
        if rolSelecionado == '1':
            tutor.objects.get_or_create(usuario=NuevoUsuario)
            
            alumno.objects.filter(usuario=NuevoUsuario).delete()
            cordinador.objects.filter(usuario=NuevoUsuario).delete()
        elif rolSelecionado == '2':
            alumno.objects.get_or_create(usuario=NuevoUsuario)
            
            tutor.objects.filter(usuario=NuevoUsuario).delete()
            cordinador.objects.filter(usuario=NuevoUsuario).delete()
        elif rolSelecionado == '3':
            cordinador.objects.get_or_create(usuario=NuevoUsuario)
            
            tutor.objects.filter(usuario=NuevoUsuario).delete()
            alumno.objects.filter(usuario=NuevoUsuario).delete()
        
        return NuevoUsuario
    
class CambiarContrasennaForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nueva contraseña'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})
        
        
class CrearHorarioForm(forms.ModelForm):
    HORA_CHOICES = [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(24)]
    hora_inicio = forms.ChoiceField(
        choices=HORA_CHOICES,
        label='Hora de Inicio',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}) )
    
    class Meta:

        model = horario
        fields = ['fecha', 'hora_inicio']
        widgets = {
            
        }

        
        
    
        
class CrearSolicitudForm(forms.ModelForm):
    class Meta:
        model = solicitud
        fields = ['motivo']
        

class SolicitidEstadoForm(forms.ModelForm):
    class Meta:
        model = solicitud
        fields = ['estado']
        

class crearFeedbackForm(forms.ModelForm):
    
    calificacion = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], label='Calificación', required=True)
    
    class Meta:
        model = Feedback
        fields = ['comentario','calificacion' ]
        
    

    
    
    
        
            
        
        