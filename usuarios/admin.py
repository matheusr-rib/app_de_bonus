from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = ('username', 'email', 'tipo', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('tipo', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser',)
        }),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
        ('Tipo de Acesso (Customizado)', {'fields': ('tipo',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'tipo', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )