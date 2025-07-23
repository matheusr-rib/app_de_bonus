from django.forms import ModelForm
from django import forms
from .models import Campanha, Banco, FaixaMeta
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

    

class CampanhaBaseForm(forms.ModelForm):
    banco_nome = forms.CharField(
        label="Banco",
        max_length=100,
        error_messages={
            'required': 'Informe o nome do banco.',
        }
    )

    class Meta:
        model = Campanha
        fields = ['campanha', 'nomenclatura_wb','anexo']
        error_messages = {
            'campanha': {
                'required': 'Informe o nome da campanha.',
            },
        } 
    
    def clean_anexo(self):
        file = self.cleaned_data.get('anexo')
        if file:
            ext = file.name.lower().split('.')[-1]
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'xlsx']:
                raise forms.ValidationError("O anexo deve ser uma imagem, PDF ou planilha Excel.")
        return file

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        if self.instance and self.instance.pk:
            self.fields['banco_nome'].initial = self.instance.banco.nome
        self.order_fields(['banco_nome', 'campanha', 'nomenclatura_wb','anexo'])

    def save(self, commit=True):
        nome_banco = self.cleaned_data.pop('banco_nome')
        banco, created = Banco.objects.get_or_create(nome=nome_banco)
        self.instance.banco = banco
        return super().save(commit=commit)
    


class Faixas_De_Meta(forms.ModelForm):
    class Meta:
        model = FaixaMeta
        fields = ['faixa_inicial', 'faixa_final', 'valor_recebido', 'tipo_valor', 'faixa_garantida']
        widgets = {
            'faixa_inicial': forms.TextInput(attrs={'placeholder': '0,00'}),
            'faixa_final': forms.TextInput(attrs={'placeholder': 'opcional'}),
            'valor_recebido': forms.TextInput(attrs={'placeholder': '0,00'}),
        }
        error_messages = {
            'faixa_inicial': {
                'required': 'Informe a faixa inicial.',
                'invalid': 'Digite um número válido para faixa inicial.',
            },
            'valor_recebido': {
                'required': 'Informe o valor recebido.',
                'invalid': 'Digite um número válido para valor recebido.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['faixa_inicial', 'faixa_final', 'valor_recebido']:
            self.fields[field].localize = True


class Recebimento_E_Repasse(forms.ModelForm):
    class Meta:
        model = Campanha
        fields = ['recebido', 'parametrizado_wb', 'tipo_valor_recebido','tipo_valor_parametrizado_wb']
        widgets = {
            'recebido': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor recebido'}),
            'parametrizado_wb': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Valor parametrizado'}),
        }
        error_messages = {
            'parametrizado_wb': {
                'required': 'Informe o valor parametrizado.',
                'invalid': 'Digite um número válido para o parametrizado.',
            },
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
    form=Faixas_De_Meta,
    fields=['faixa_inicial', 'faixa_final', 'tipo_valor', 'valor_recebido', 'faixa_garantida'],
    extra=1,
    can_delete=True
)