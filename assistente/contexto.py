"""Contexto enviado à IA: o arquivo contexto_projeto.md + dados atuais do usuário.

Só vão os registros DO PRÓPRIO usuário que pergunta (totais e os
medicamentos com validade próxima) — nunca dados de outros usuários.
"""
from datetime import timedelta
from functools import lru_cache
from pathlib import Path

from django.utils import timezone

from farmacia.models import Distribuidora, Laboratorio, Medicamento, ProdutoDiverso

ARQUIVO_CONTEXTO = Path(__file__).resolve().parent / 'contexto_projeto.md'
LIMITE_MEDICAMENTOS = 10
DIAS_ALERTA = 30


@lru_cache(maxsize=1)
def contexto_fixo():
    return ARQUIVO_CONTEXTO.read_text(encoding='utf-8').strip()


def dados_do_usuario(usuario):
    hoje = timezone.localdate()
    meds = Medicamento.objects.filter(cadastrado_por=usuario)
    alerta = list(
        meds.filter(data_validade__lte=hoje + timedelta(days=DIAS_ALERTA))
        .select_related('laboratorio')
        .order_by('data_validade')[:LIMITE_MEDICAMENTOS]
    )
    if alerta:
        linhas_alerta = '\n'.join(
            f'- {m.nome} (lote {m.lote}, laboratório {m.laboratorio.nome}): validade {m.data_validade:%d/%m/%Y}'
            f'{" — VENCIDO" if m.data_validade < hoje else ""}'
            for m in alerta
        )
    else:
        linhas_alerta = '- nenhum medicamento vencido ou vencendo nos próximos 30 dias'
    return (
        f'## Dados atuais do usuário {usuario.username} (hoje é {hoje:%d/%m/%Y})\n\n'
        f'- Medicamentos cadastrados: {meds.count()} '
        f'({meds.filter(controlado=True).count()} controlados, '
        f'{meds.filter(data_validade__lt=hoje).count()} vencidos)\n'
        f'- Produtos diversos: {ProdutoDiverso.objects.filter(cadastrado_por=usuario).count()}\n'
        f'- Laboratórios: {Laboratorio.objects.filter(cadastrado_por=usuario).count()}\n'
        f'- Distribuidoras: {Distribuidora.objects.filter(cadastrado_por=usuario).count()}\n\n'
        f'### Medicamentos vencidos ou que vencem em até {DIAS_ALERTA} dias (até {LIMITE_MEDICAMENTOS})\n'
        f'{linhas_alerta}'
    )


def montar_contexto(usuario):
    return f'{contexto_fixo()}\n\n{dados_do_usuario(usuario)}'
