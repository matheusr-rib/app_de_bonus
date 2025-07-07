from django.views.generic import ListView, View, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from usuarios.decorators import tipo_usuario_requerido
from django.db.models import Q

from .models import Campanha
from .forms import (
    CampanhaBaseForm,
    Recebimento_E_Repasse,
    VigenciaERegras,
    FaixaMetaFormSet
)


@method_decorator(login_required(login_url='login'), name='dispatch')
class CampanhaListView(ListView):
    model = Campanha
    template_name = 'campanha_list.html'
    context_object_name = 'campanhas'

    def get_queryset(self):
        queryset = super().get_queryset()

        termo_busca = self.request.GET.get('q')
        status_filtro = self.request.GET.get('status')

        if termo_busca:
            queryset = queryset.filter(
                Q(campanha__icontains=termo_busca) |
                Q(banco__nome__icontains=termo_busca)
            )

        if status_filtro and status_filtro != 'todas':
            queryset = queryset.filter(status_manual__iexact=status_filtro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', 'todas')
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(tipo_usuario_requerido('master', 'editor'), name='dispatch')
class CampanhaCreateView(View):
    """Cria uma campanha e, opcionalmente, várias FaixaMeta.

    A ordem correta é:
      1. Validar os formulários principais.
      2. Salvar a campanha para obter o PK.
      3. Reinstanciar o formset **com** `instance` e validá‑lo.
      4. Salvar o formset.
    """

    template_name = 'campanha_form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form_campanha': CampanhaBaseForm(),
            'form_recebimento': Recebimento_E_Repasse(),
            'form_vigencia': VigenciaERegras(),
            'faixa_formset': FaixaMetaFormSet(prefix='faixas')
        })

    def post(self, request):
        form_campanha = CampanhaBaseForm(request.POST)
        form_recebimento = Recebimento_E_Repasse(request.POST)
        form_vigencia = VigenciaERegras(request.POST)
        possui_meta = request.POST.get('possui_meta') == 'on'

        # Valida primeiro os formulários principais
        if form_campanha.is_valid() and form_recebimento.is_valid() and form_vigencia.is_valid():
            # 1️⃣ Salva a campanha para obter o PK
            campanha = form_campanha.save(commit=False)

            campanha.recebido = form_recebimento.cleaned_data.get('recebido')
            campanha.parametrizado_wb = form_recebimento.cleaned_data.get('parametrizado_wb')
            campanha.tipo_valor_recebido = form_recebimento.cleaned_data.get('tipo_valor_recebido')
            campanha.tipo_valor_parametrizado_wb = form_recebimento.cleaned_data.get('tipo_valor_parametrizado_wb')

            campanha.vigencia_inicio = form_vigencia.cleaned_data.get('vigencia_inicio')
            campanha.vigencia_fim = form_vigencia.cleaned_data.get('vigencia_fim')
            campanha.periodicidade_repasses = form_vigencia.cleaned_data.get('periodicidade_repasses')
            campanha.previsao_pagamento = form_vigencia.cleaned_data.get('previsao_pagamento')
            campanha.parametro_avaliacao = form_vigencia.cleaned_data.get('parametro_avaliacao')
            campanha.criterio_apuracao = form_vigencia.cleaned_data.get('criterio_apuracao')
            campanha.observacoes = form_vigencia.cleaned_data.get('observacoes')
            campanha.status_manual = form_vigencia.cleaned_data.get('status_manual')

            campanha.possui_meta = possui_meta
            campanha.save()

            # 2️⃣ Reinstancia o formset AGORA com a instância salva
            faixa_formset = FaixaMetaFormSet(request.POST, instance=campanha, prefix='faixas')

            # 3️⃣ Valida e salva as faixas
            if possui_meta:
                if faixa_formset.is_valid():
                    faixa_formset.save()
                else:
                    # Se as faixas estiverem inválidas, volta ao form com erros
                    return render(request, self.template_name, {
                        'form_campanha': form_campanha,
                        'form_recebimento': form_recebimento,
                        'form_vigencia': form_vigencia,
                        'faixa_formset': faixa_formset
                    })

            return redirect('campanha_list')

        # Se qualquer form principal for inválido, monta o formset vazio para exibir
        faixa_formset = FaixaMetaFormSet(request.POST, prefix='faixas')
        return render(request, self.template_name, {
            'form_campanha': form_campanha,
            'form_recebimento': form_recebimento,
            'form_vigencia': form_vigencia,
            'faixa_formset': faixa_formset
        })


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(tipo_usuario_requerido('master', 'editor'), name='dispatch')
class CampanhaUpdateView(View):
    template_name = 'campanha_form.html'

    def get(self, request, pk):
        campanha = get_object_or_404(Campanha, pk=pk)
        return render(request, self.template_name, {
            'form_campanha': CampanhaBaseForm(instance=campanha),
            'form_recebimento': Recebimento_E_Repasse(instance=campanha),
            'form_vigencia': VigenciaERegras(instance=campanha),
            'faixa_formset': FaixaMetaFormSet(instance=campanha, prefix='faixas')
        })

    def post(self, request, pk):
        campanha = get_object_or_404(Campanha, pk=pk)
        form_campanha = CampanhaBaseForm(request.POST, instance=campanha)
        form_recebimento = Recebimento_E_Repasse(request.POST, instance=campanha)
        form_vigencia = VigenciaERegras(request.POST, instance=campanha)
        faixa_formset = FaixaMetaFormSet(request.POST, instance=campanha, prefix='faixas')
        possui_meta = request.POST.get('possui_meta') == 'on'

        if all([
            form_campanha.is_valid(),
            form_recebimento.is_valid(),
            form_vigencia.is_valid(),
            faixa_formset.is_valid()
        ]):
            campanha = form_campanha.save(commit=False)

            campanha.recebido = form_recebimento.cleaned_data.get('recebido')
            campanha.parametrizado_wb = form_recebimento.cleaned_data.get('parametrizado_wb')
            campanha.tipo_valor_recebido = form_recebimento.cleaned_data.get('tipo_valor_recebido')
            campanha.tipo_valor_parametrizado_wb = form_recebimento.cleaned_data.get('tipo_valor_parametrizado_wb')

            campanha.vigencia_inicio = form_vigencia.cleaned_data.get('vigencia_inicio')
            campanha.vigencia_fim = form_vigencia.cleaned_data.get('vigencia_fim')
            campanha.periodicidade_repasses = form_vigencia.cleaned_data.get('periodicidade_repasses')
            campanha.previsao_pagamento = form_vigencia.cleaned_data.get('previsao_pagamento')
            campanha.parametro_avaliacao = form_vigencia.cleaned_data.get('parametro_avaliacao')
            campanha.criterio_apuracao = form_vigencia.cleaned_data.get('criterio_apuracao')
            campanha.observacoes = form_vigencia.cleaned_data.get('observacoes')
            campanha.status_manual = form_vigencia.cleaned_data.get('status_manual')

            campanha.possui_meta = possui_meta
            campanha.save()

            if possui_meta:
                faixa_formset.save()

            return redirect('campanha_list')

        return render(request, self.template_name, {
            'form_campanha': form_campanha,
            'form_recebimento': form_recebimento,
            'form_vigencia': form_vigencia,
            'faixa_formset': faixa_formset
        })


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(tipo_usuario_requerido('master', 'editor'), name='dispatch')
class CampanhaDeleteView(DeleteView):
    model = Campanha
    template_name = 'campanha_confirm_delete.html'
    success_url = reverse_lazy('campanha_controle')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Apaga as faixas ligadas primeiro
        self.object.faixas.all().delete()

        # Agora pode deletar a campanha
        self.object.delete()
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
@method_decorator(tipo_usuario_requerido('editor', 'master'), name='dispatch')
class CampanhaControleView(ListView):
    model = Campanha
    template_name = 'campanha_controle.html'
    context_object_name = 'campanhas'
