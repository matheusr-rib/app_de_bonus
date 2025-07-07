from django.db import models
from django.utils import timezone
from historico.middleware import get_current_request

class Banco(models.Model):
    nome = models.CharField(max_length=100, default='Banco Genérico')

    def __str__(self):
        return self.nome


class Campanha(models.Model):
    TIPO_VALOR_CHOICES = [
        ('R$', 'R$'),
        ('%', '%'),
    ]

    STATUS_MANUAL_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('INATIVA', 'Inativa'),
        ('EM ANALISE', 'Em analise'),
    ]

    banco = models.ForeignKey(Banco, on_delete=models.PROTECT, related_name='campanhas')
    campanha = models.CharField(max_length=200, default=' ')
    nomenclatura_wb = models.CharField(max_length=200, default=' ')
    recebido = models.CharField(max_length=200, default=' ', blank=True, null=True)
    parametrizado_wb = models.CharField(max_length=200, default=' ', blank=True, null=True)
    tipo_valor_recebido = models.CharField(max_length=20, choices=TIPO_VALOR_CHOICES, default='%', blank=True, null=True)
    tipo_valor_parametrizado_wb = models.CharField(max_length=20, choices=TIPO_VALOR_CHOICES, default=' ', blank=True, null=True)

    vigencia_inicio = models.DateField(default=timezone.now)
    vigencia_fim = models.DateField(blank=True, null=True)
    periodicidade_repasses = models.CharField(max_length=100, default=' ')
    previsao_pagamento = models.CharField(max_length=100,blank=True, null=True)
    parametro_avaliacao = models.TextField(default=' ')
    criterio_apuracao = models.TextField(default=' ')
    observacoes = models.TextField(blank=True, null=True)

    possui_meta = models.BooleanField(default=False)
    tem_garantido = models.BooleanField(default=False)

    status_manual = models.CharField(max_length=50, choices=STATUS_MANUAL_CHOICES, default='ATIVA')

    def __str__(self):
        return f"{self.campanha} ({self.banco})"
    
    def save(self, *args, **kwargs):
        self._request = get_current_request()
        super().save(*args, **kwargs)



class FaixaMeta(models.Model):
    campanha = models.ForeignKey('Campanha', on_delete=models.CASCADE, related_name='faixas')
    faixa_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    faixa_final = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    tipo_valor = models.CharField(max_length=10, choices=[('R$', 'R$'), ('%', '%')], default='%')
    valor_recebido = models.DecimalField(max_digits=12, decimal_places=2)
    faixa_garantida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.faixa_inicial} - {self.faixa_final or 'acima'}"
