from django.db import models
from django.conf import settings
from campanhas.models import Campanha
from historico.middleware import get_current_request


class HistoricoAcao(models.Model):
    ACAO_CHOICES = (
        ('criado', 'Criado'),
        ('editado', 'Editado'),
        ('deletado', 'Deletado'),
    )

    campanha = models.ForeignKey('campanhas.Campanha', on_delete=models.SET_NULL, null=True, blank=True)
    campanha_nome = models.CharField(max_length=255, blank=True)  # salva o nome da campanha
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=10, choices=ACAO_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)
    vigencia_inicio = models.DateField(blank=True, null=True)
    vigencia_fim = models.DateField(blank=True, null=True)
    detalhe = models.TextField(blank=True)

    def __str__(self):
        return f"{self.campanha_nome} - {self.acao} por {self.usuario} em {self.data_hora}"



def save(self, *args, **kwargs):
    self._request = get_current_request()
    super().save(*args, **kwargs)