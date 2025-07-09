from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from historico.models import HistoricoAcao
from django.core.paginator import Paginator
from django.db.models import Q
from campanhas.models import Banco
from usuarios.decorators import tipo_usuario_requerido
from django.utils.decorators import method_decorator


@login_required(login_url='login')
@tipo_usuario_requerido('master')
def historico_listagem(request):
    queryset = HistoricoAcao.objects.select_related('campanha', 'usuario')

    # Filtros
    nome = request.GET.get('nome')
    banco_id = request.GET.get('banco')
    usuario_id = request.GET.get('usuario')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status')

    if status:
        queryset = queryset.filter(campanha__status_manual=status)
    if nome:
        queryset = queryset.filter(campanha__campanha__icontains=nome)
    if banco_id:
        queryset = queryset.filter(campanha__banco_id=banco_id)
    if usuario_id:
        queryset = queryset.filter(usuario_id=usuario_id)
    if data_inicio:
        queryset = queryset.filter(vigencia_inicio__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(vigencia_fim__lte=data_fim)

    paginator = Paginator(queryset.order_by('-data_hora'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    bancos = Banco.objects.all()
    usuarios = queryset.values_list('usuario__id', 'usuario__username').distinct()

    status_choices = [
    ('ATIVA', 'Ativa'),
    ('INATIVA', 'Inativa'),
    ('EM ANALISE', 'Em análise'),
    ]

    context = {
        'page_obj': page_obj,
        'bancos': bancos,
        'usuarios': usuarios,
        'status_choices': status_choices,
    }
    return render(request, 'historico_listagem.html', context)