from django.db import models
from django.conf import settings
from campanhas.models import Campanha
from historico.middleware import get_current_request
from django.conf import settings



class HistoricoAcao(models.Model):
    campanha = models.ForeignKey(
        Campanha,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historicos'
    )
    campanha_nome = models.CharField(max_length=255)
    acao = models.CharField(max_length=50)
    usuario = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    null=True,
    blank=True,
    on_delete=models.SET_NULL
    )
    vigencia_inicio = models.DateField(null=True, blank=True)
    vigencia_fim = models.DateField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    detalhe = models.TextField(blank=True)

    def __str__(self):
        return f"{self.acao} - {self.campanha_nome}"



def save(self, *args, **kwargs):
    self._request = get_current_request()
    super().save(*args, **kwargs)