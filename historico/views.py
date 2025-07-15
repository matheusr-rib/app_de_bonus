from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from historico.models import HistoricoAcao
from django.core.paginator import Paginator
from django.db.models import Q
from campanhas.models import Banco
from usuarios.decorators import tipo_usuario_requerido
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from campanhas.models import Campanha
from datetime import datetime


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

@login_required(login_url='login')
@tipo_usuario_requerido('master')
def relatorios_campanha(request):
    context = {
        'bancos': Campanha.objects.values_list('banco__id', 'banco__nome').distinct(),
        'usuarios': HistoricoAcao.objects.values_list('usuario__id', 'usuario__username').distinct(),
        'status_choices': [
            ('ATIVA', 'Ativa'),
            ('INATIVA', 'Inativa'),
            ('EM ANALISE', 'Em análise'),
        ]
    }
    return render(request, 'relatorios_campanha.html', context)

@login_required(login_url='login')
@tipo_usuario_requerido('master')
def exportar_relatorio_excel(request):
    tipo = request.GET.get("tipo", "alteracoes")
    wb = Workbook()
    ws = wb.active

    if tipo == "vigencias":
        ws.title = "Relatório de Vigências"
        headers = ["Banco", "Campanha", "Status", "Vigência Início", "Vigência Fim", "Data de Exclusão"]
        ws.append(headers)

        campanhas = Campanha.objects.select_related("banco")

        # Filtros
        nome = request.GET.get("nome")
        banco_id = request.GET.get("banco")
        status = request.GET.get("status")
        data_inicio = request.GET.get("data_inicio")
        data_fim = request.GET.get("data_fim")

        if nome:
            campanhas = campanhas.filter(campanha__icontains=nome)
        if banco_id:
            campanhas = campanhas.filter(banco_id=banco_id)
        if status:
            campanhas = campanhas.filter(status_manual=status)

        # Filtro de vigência corrigido
        if data_inicio and data_fim:
            campanhas = campanhas.filter(
                vigencia_inicio__lte=data_fim
            ).filter(
                Q(vigencia_fim__gte=data_inicio) | Q(vigencia_fim__isnull=True)
            )
        elif data_inicio:
            campanhas = campanhas.filter(
                Q(vigencia_fim__gte=data_inicio) | Q(vigencia_fim__isnull=True)
            )
        elif data_fim:
            campanhas = campanhas.filter(vigencia_inicio__lte=data_fim)

        # Data de exclusão (baseado no histórico)
        historico_deletadas = HistoricoAcao.objects.filter(acao='deletado')
        historico_exclusoes = {h.campanha_nome: h.data_hora.date() for h in historico_deletadas}

        for c in campanhas:
            vigencia_inicio = c.vigencia_inicio.strftime("%d/%m/%Y") if c.vigencia_inicio else ""
            vigencia_fim = c.vigencia_fim.strftime("%d/%m/%Y") if c.vigencia_fim else "—"
            data_exclusao = historico_exclusoes.get(c.campanha)
            data_exclusao_fmt = data_exclusao.strftime("%d/%m/%Y") if data_exclusao else ""

            ws.append([
                c.banco.nome,
                c.campanha,
                c.status_manual,
                vigencia_inicio,
                vigencia_fim,
                data_exclusao_fmt
            ])

    else:  # tipo == "alteracoes"
        ws.title = "Relatório de Alterações"
        headers = [
            "ID", "Banco", "Campanha", "Status", "Ação", "Usuário",
            "Vigência Início", "Vigência Fim", "Data da Ação", "Detalhe"
        ]
        ws.append(headers)

        historicos = HistoricoAcao.objects.select_related("campanha", "usuario", "campanha__banco")

        nome = request.GET.get("nome")
        banco_id = request.GET.get("banco")
        usuario_id = request.GET.get("usuario")
        status = request.GET.get("status")
        data_acao_inicio = request.GET.get("data_acao_inicio")
        data_acao_fim = request.GET.get("data_acao_fim")

        if nome:
            historicos = historicos.filter(campanha_nome__icontains=nome)
        if banco_id:
            historicos = historicos.filter(campanha__banco_id=banco_id)
        if usuario_id:
            historicos = historicos.filter(usuario_id=usuario_id)
        if status:
            historicos = historicos.filter(campanha__status_manual=status)
        if data_acao_inicio and data_acao_fim:
            historicos = historicos.filter(data_hora__date__range=[data_acao_inicio, data_acao_fim])
        elif data_acao_inicio:
            historicos = historicos.filter(data_hora__date__gte=data_acao_inicio)
        elif data_acao_fim:
            historicos = historicos.filter(data_hora__date__lte=data_acao_fim)

        for h in historicos.order_by("-data_hora"):
            campanha = h.campanha
            banco = campanha.banco.nome if campanha else "—"
            status = campanha.status_manual if campanha else "—"
            vig_inicio = h.vigencia_inicio.strftime("%d/%m/%Y") if h.vigencia_inicio else ""
            vig_fim = h.vigencia_fim.strftime("%d/%m/%Y") if h.vigencia_fim else "—"
            data_acao = h.data_hora.strftime("%d/%m/%Y %H:%M")

            ws.append([
                h.id,
                banco,
                h.campanha_nome,
                status,
                h.acao,
                h.usuario.username if h.usuario else "Sistema",
                vig_inicio,
                vig_fim,
                data_acao,
                h.detalhe
            ])

    # Ajustar largura automática das colunas
    for col in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # Geração do arquivo
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"relatorio_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response