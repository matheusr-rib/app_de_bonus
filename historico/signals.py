from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from campanhas.models import Campanha
from historico.models import HistoricoAcao
from historico.middleware import get_current_request


@receiver(post_save, sender=Campanha)
def registrar_historico_criacao_ou_edicao(sender, instance, created, **kwargs):
    request = get_current_request()
    if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
        return

    acao = 'criado' if created else 'editado'
    HistoricoAcao.objects.create(
        campanha=instance,
        campanha_nome=instance.campanha,
        usuario=request.user,
        acao=acao,
        detalhe=f"Campanha {acao} via interface web",
        vigencia_inicio=instance.vigencia_inicio,
        vigencia_fim=instance.vigencia_fim,
    )


@receiver(post_delete, sender=Campanha)
def registrar_historico_exclusao(sender, instance, **kwargs):
    request = get_current_request()
    if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
        return

    HistoricoAcao.objects.create(
        campanha=None,
        campanha_nome=instance.campanha,
        usuario=request.user,
        acao='deletado',
        detalhe="Campanha excluída via interface web",
        vigencia_inicio=instance.vigencia_inicio,
        vigencia_fim=instance.vigencia_fim,
    )