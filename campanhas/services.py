from datetime import date
from campanhas.models import Campanha
from historico.models import HistoricoAcao

def atualizar_campanhas_expiradas():
    hoje = date.today()

    campanhas_ativas = Campanha.objects.filter(
        status_manual='ATIVA',
        vigencia_fim__lt=hoje,
        inativada_automaticamente=False  # ✅ nova verificação
    )

    for campanha in campanhas_ativas:
        # ✅ Atualiza status e marca como inativada
        campanha.status_manual = 'INATIVA'
        campanha.inativada_automaticamente = True
        campanha.save(update_fields=['status_manual', 'inativada_automaticamente'])

        # ✍️ Registra no histórico
        HistoricoAcao.objects.create(
            campanha=campanha,
            campanha_nome=campanha.campanha,
            usuario=None,  # Ação automática
            acao='editado',
            detalhe='Status inativado automaticamente por término da vigência.',
            vigencia_inicio=campanha.vigencia_inicio,
            vigencia_fim=campanha.vigencia_fim,
        )
