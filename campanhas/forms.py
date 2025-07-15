from django.forms import ModelForm
from django import forms
from .models import Campanha, Banco, FaixaMeta
from django.forms import inlineformset_factory

class CampanhaBaseForm(forms.ModelForm):
    banco_nome = forms.CharField(label="Banco", max_length=100)

    class Meta:
        model = Campanha
        fields = ['campanha', 'nomenclatura_wb']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        if self.instance and self.instance.pk:
            self.fields['banco_nome'].initial = self.instance.banco.nome
        self.order_fields(['banco_nome', 'campanha', 'nomenclatura_wb'])

    def save(self, commit=True):
        nome_banco = self.cleaned_data.pop('banco_nome')
        banco, created = Banco.objects.get_or_create(nome=nome_banco)
        self.instance.banco = banco
        return super().save(commit=commit)


class Faixas_De_Meta(forms.ModelForm):
    class Meta:
        model = FaixaMeta
        fields = [
            'faixa_inicial',
            'faixa_final',
            'valor_recebido',
            'tipo_valor',
            'faixa_garantida'
        ]
        widgets = {
            'faixa_inicial': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor mínimo'}),
            'faixa_final': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor máximo'}),
            'valor_recebido': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor recebido'}),
        }


class Recebimento_E_Repasse(ModelForm):
    class Meta:
        model = Campanha
        fields = ['recebido', 'parametrizado_wb', 'tipo_valor_recebido','tipo_valor_parametrizado_wb']
        widgets = {
            'recebido': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor recebido'}),
            'parametrizado_wb': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor parametrizado'}),
        }


class VigenciaERegras(ModelForm):
    class Meta:
        model = Campanha
        fields = [
            'vigencia_inicio', 'vigencia_fim','periodicidade_repasses',
            'previsao_pagamento','parametro_avaliacao','criterio_apuracao',
            'observacoes','status_manual','parametro_pagamento',
        ]
        widgets = {
            'vigencia_inicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'vigencia_fim': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detalhes adicionais...'}),
        }


FaixaMetaFormSet = inlineformset_factory(
    Campanha,
    FaixaMeta,
    fields=['faixa_inicial', 'faixa_final', 'tipo_valor', 'valor_recebido', 'faixa_garantida'],
    extra=1,
    can_delete=True,  
    widgets={
        'faixa_inicial': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        'faixa_final': forms.NumberInput(attrs={'placeholder': 'opcional', 'step': '0.01'}),
        'valor_recebido': forms.NumberInput(attrs={'placeholder': 'Ex: 0.50', 'step': '0.01'}),
    }
)