from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from historico.models import HistoricoAcao
from django.core.paginator import Paginator
from django.db.models import Q
from campanhas.models import Banco

@login_required
def historico_listagem(request):
    queryset = HistoricoAcao.objects.select_related('campanha', 'usuario')

    # Filtros
    nome = request.GET.get('nome')
    banco_id = request.GET.get('banco')
    usuario_id = request.GET.get('usuario')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if nome:
        queryset = queryset.filter(campanha__campanha__icontains=nome)
    if banco_id:
        queryset = queryset.filter(campanha__banco_id=banco_id)
    if usuario_id:
        queryset = queryset.filter(usuario_id=usuario_id)
    if data_inicio and data_fim:
        queryset = queryset.filter(data_hora__range=[data_inicio, data_fim])

    paginator = Paginator(queryset.order_by('-data_hora'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    bancos = Banco.objects.all()
    usuarios = queryset.values_list('usuario__id', 'usuario__username').distinct()

    context = {
        'page_obj': page_obj,
        'bancos': bancos,
        'usuarios': usuarios,
    }
    return render(request, 'historico_listagem.html', context)