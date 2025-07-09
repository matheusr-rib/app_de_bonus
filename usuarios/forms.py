from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UsuarioCreateForm(UserCreationForm):
    tipo = forms.ChoiceField(
        choices=Usuario.TIPO_CHOICES,
        label="Tipo de Usuário"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'tipo', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'border border-gray-400 rounded w-full p-2'}),
            'password1': forms.PasswordInput(attrs={'class': 'border border-gray-400 rounded w-full p-2'}),
            'password2': forms.PasswordInput(attrs={'class': 'border border-gray-400 rounded w-full p-2'}),
            'tipo': forms.Select(attrs={'class': 'border border-gray-400 rounded w-full p-2'}),
        }