from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Direccion, Reseña

class RegistroForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        }),
        error_messages={
            'required': 'El nombre de usuario es requerido',
            'max_length': 'El nombre de usuario no puede tener más de 150 caracteres'
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
        error_messages={
            'required': 'El correo electrónico es requerido',
            'invalid': 'Ingresa un correo electrónico válido'
        }
    )
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        error_messages={
            'required': 'La contraseña es requerida',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    password_confirm = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        error_messages={
            'required': 'La confirmación de contraseña es requerida',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('El usuario ya existe')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('El email ya está registrado')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return cleaned_data

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre', 'apellido', 'direccion', 'ciudad', 'departamento', 'codigo_postal', 'telefono', 'es_predeterminada']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de envío'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Departamento'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código postal'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'es_predeterminada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CheckoutForm(forms.Form):
    direccion_existente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe tu dirección completa'}),
        label='Escribe tu dirección'
    )
    usar_direccion_nueva = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Usar una dirección nueva'
    )
    metodo_pago = forms.ChoiceField(
        choices=[('stripe', 'Tarjeta de crédito/débito'), ('contra_entrega', 'Contra entrega')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='stripe'
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales para tu pedido'}),
        label='Notas adicionales'
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['direccion_existente'].queryset = Direccion.objects.filter(usuario=usuario)

class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu reseña aquí...'}),
        }
