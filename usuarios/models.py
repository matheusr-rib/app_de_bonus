from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_CHOICES = (
        ('master', 'Master'),
        ('editor', 'Editor'),
        ('visualizador', 'Visualizador'),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='visualizador')

    def __str__(self):
        return f"{self.username} ({self.tipo})"