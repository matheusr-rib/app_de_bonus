from django.views.generic import ListView, View, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from usuarios.decorators import tipo_usuario_requerido
from django.db.models import Q
from historico.models import HistoricoAcao
from .services import atualizar_campanhas_expiradas
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
        atualizar_campanhas_expiradas()

        queryset = super().get_queryset()

        nome = self.request.GET.get('nome')
        banco = self.request.GET.get('banco')
        status = self.request.GET.get('status')
        data_inicio = self.request.GET.get('vigencia_inicio')
        data_fim = self.request.GET.get('vigencia_fim')

        if nome:
            queryset = queryset.filter(campanha__icontains=nome)

        if banco:
            queryset = queryset.filter(banco__nome__icontains=banco)

        # Aplica status padrão se nada for informado
        if status is None:
            queryset = queryset.filter(status_manual__iexact='ATIVA')
        elif status != 'todas':
            queryset = queryset.filter(status_manual__iexact=status)

        if data_inicio and data_fim:
            queryset = queryset.filter(
                vigencia_inicio__lte=data_fim,
                vigencia_fim__gte=data_inicio
            )
        elif data_inicio:
            queryset = queryset.filter(vigencia_fim__gte=data_inicio)
        elif data_fim:
            queryset = queryset.filter(vigencia_inicio__lte=data_fim)

        return queryset.order_by('banco__nome', 'campanha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filtro_nome'] = self.request.GET.get('nome', '')
        context['filtro_banco'] = self.request.GET.get('banco', '')
        context['filtro_status'] = self.request.GET.get('status', 'ATIVA')
        context['filtro_vigencia_inicio'] = self.request.GET.get('vigencia_inicio', '')
        context['filtro_vigencia_fim'] = self.request.GET.get('vigencia_fim', '')

        context['status_labels'] = (
            Campanha.objects
            .values_list('status_manual', flat=True)
            .distinct()
            .order_by('status_manual')
        )

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filtro_nome'] = self.request.GET.get('nome', '')
        context['filtro_banco'] = self.request.GET.get('banco', '')
        context['filtro_status'] = self.request.GET.get('status', 'ATIVA')
        context['filtro_vigencia_inicio'] = self.request.GET.get('vigencia_inicio', '')
        context['filtro_vigencia_fim'] = self.request.GET.get('vigencia_fim', '')

        context['status_labels'] = (
            Campanha.objects
            .values_list('status_manual', flat=True)
            .distinct()
            .order_by('status_manual')
        )

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
            campanha.parametro_pagamento = form_vigencia.cleaned_data.get('parametro_pagamento')
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
                    print('❌ ERROS NO FORMSET:')
                    for form in faixa_formset:
                        print(form.errors)
                    print(faixa_formset.non_form_errors())
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
        possui_meta = 'possui_meta' in request.POST or campanha.possui_meta
        faixa_formset = FaixaMetaFormSet(request.POST, instance=campanha, prefix='faixas')

        if form_campanha.is_valid() and form_recebimento.is_valid() and form_vigencia.is_valid():
            campanha = form_campanha.save(commit=False)

            # Campos adicionais
            campanha.recebido = form_recebimento.cleaned_data.get('recebido')
            campanha.parametrizado_wb = form_recebimento.cleaned_data.get('parametrizado_wb')
            campanha.tipo_valor_recebido = form_recebimento.cleaned_data.get('tipo_valor_recebido')
            campanha.tipo_valor_parametrizado_wb = form_recebimento.cleaned_data.get('tipo_valor_parametrizado_wb')

            campanha.vigencia_inicio = form_vigencia.cleaned_data.get('vigencia_inicio')
            campanha.vigencia_fim = form_vigencia.cleaned_data.get('vigencia_fim')
            campanha.periodicidade_repasses = form_vigencia.cleaned_data.get('periodicidade_repasses')
            campanha.previsao_pagamento = form_vigencia.cleaned_data.get('previsao_pagamento')
            campanha.parametro_avaliacao = form_vigencia.cleaned_data.get('parametro_avaliacao')
            campanha.parametro_pagamento = form_vigencia.cleaned_data.get('parametro_pagamento')
            campanha.criterio_apuracao = form_vigencia.cleaned_data.get('criterio_apuracao')
            campanha.observacoes = form_vigencia.cleaned_data.get('observacoes')
            campanha.status_manual = form_vigencia.cleaned_data.get('status_manual')

            campanha.possui_meta = possui_meta
            campanha.save()

            # 🔁 AGORA instanciamos o formset com a instância salva
            faixa_formset = FaixaMetaFormSet(request.POST, instance=campanha, prefix='faixas')

            if possui_meta:
                if faixa_formset.is_valid():
                    faixa_formset.save()
                else:
                    print('📛 Formset inválido:')
                    print(faixa_formset.errors)
                    print(faixa_formset.non_form_errors())
                    return render(request, self.template_name, {
                        'form_campanha': form_campanha,
                        'form_recebimento': form_recebimento,
                        'form_vigencia': form_vigencia,
                        'faixa_formset': faixa_formset
                    })
            else:
                campanha.faixas.all().delete()

            return redirect('campanha_list')

        # Se algum form principal for inválido
        faixa_formset = FaixaMetaFormSet(request.POST, instance=campanha, prefix='faixas')
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

        # 💾 Salvar o histórico ANTES da exclusão
        if request.user.is_authenticated:
            HistoricoAcao.objects.create(
            campanha=None,  # campanha vai virar nula após exclusão
            campanha_nome=self.object.campanha,
            usuario=request.user,
            acao='deletado',
            detalhe="Campanha deletada via interface web",
            vigencia_inicio=self.object.vigencia_inicio,
            vigencia_fim=self.object.vigencia_fim,
            )

        # Deleta faixas relacionadas primeiro
        self.object.faixas.all().delete()

        # Agora deleta a campanha
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(tipo_usuario_requerido('editor', 'master'), name='dispatch')
class CampanhaControleView(ListView):
    model = Campanha
    template_name = 'campanha_controle.html'
    context_object_name = 'campanhas'

    def get_queryset(self):
        atualizar_campanhas_expiradas()

        queryset = super().get_queryset()

        nome = self.request.GET.get('nome')
        banco = self.request.GET.get('banco')
        status = self.request.GET.get('status')
        data_inicio = self.request.GET.get('vigencia_inicio')
        data_fim = self.request.GET.get('vigencia_fim')

        if nome:
            queryset = queryset.filter(campanha__icontains=nome)

        if banco:
            queryset = queryset.filter(banco__nome__icontains=banco)

        if status is None:
            queryset = queryset.filter(status_manual__iexact='ATIVA')
        elif status != 'todas':
            queryset = queryset.filter(status_manual__iexact=status)

        if data_inicio and data_fim:
            queryset = queryset.filter(
                vigencia_inicio__lte=data_fim,
                vigencia_fim__gte=data_inicio
            )
        elif data_inicio:
            queryset = queryset.filter(vigencia_fim__gte=data_inicio)
        elif data_fim:
            queryset = queryset.filter(vigencia_inicio__lte=data_fim)

        return queryset.order_by('banco__nome', 'campanha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filtro_nome'] = self.request.GET.get('nome', '')
        context['filtro_banco'] = self.request.GET.get('banco', '')
        context['filtro_status'] = self.request.GET.get('status', 'ATIVA')
        context['filtro_vigencia_inicio'] = self.request.GET.get('vigencia_inicio', '')
        context['filtro_vigencia_fim'] = self.request.GET.get('vigencia_fim', '')

        context['status_opcoes'] = (
            Campanha.objects
            .values_list('status_manual', flat=True)
            .distinct()
            .order_by('status_manual')
        )

        return context