# tests/e2e/test_leilao_e2e.py
from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from datetime import datetime, timedelta
from models.leilao import Leilao
from models.participante import Participante
from models.lance import Lance

# Carrega os cenários do arquivo .feature
scenarios('gerenciamento_leilao.feature')

# Fixtures para compartilhar dados entre os passos
@pytest.fixture
def context():
    return {}

@given(parsers.parse('um leilão chamado "{nome_leilao}" está cadastrado com lance mínimo de {lance_minimo:f}'))
def setup_leilao(sistema_limpo, context, nome_leilao, lance_minimo):
    agora = datetime.now()
    leilao = Leilao(
        nome=nome_leilao,
        lance_minimo=lance_minimo,
        data_inicio=agora,
        data_fim=agora + timedelta(hours=1)
    )
    context['leilao'] = sistema_limpo.adicionar_leilao(leilao)

@given(parsers.parse('um participante chamado "{nome_participante}" está cadastrado'))
def setup_participante(sistema_limpo, context, nome_participante):
    participante = Participante(
        cpf=f"111.111.111-{datetime.now().microsecond % 100:02d}", # CPF único para cada teste
        nome=nome_participante,
        email=f"{nome_participante.lower()}@test.com",
        data_nascimento=datetime(1990, 1, 1)
    )
    context['participante'] = sistema_limpo.adicionar_participante(participante)

@when(parsers.parse('o leilão "{nome_leilao}" é aberto'))
def abrir_leilao(sistema_limpo, context, nome_leilao):
    assert context['leilao'].nome == nome_leilao
    sistema_limpo.abrir_leilao(context['leilao'].id, datetime.now())

@when(parsers.parse('"{nome_participante}" dá um lance de {valor:f} no leilão "{nome_leilao}"'))
def dar_lance(sistema_limpo, context, nome_participante, valor, nome_leilao):
    assert context['leilao'].nome == nome_leilao
    assert context['participante'].nome == nome_participante
    
    lance = Lance(
        valor=valor,
        participante_id=context['participante'].id,
        leilao_id=context['leilao'].id,
        data_hora=datetime.now()
    )
    sistema_limpo.adicionar_lance(context['leilao'].id, lance)
    context['ultimo_lance'] = lance

@when(parsers.parse('o leilão "{nome_leilao}" é finalizado'))
def finalizar_leilao(sistema_limpo, context, nome_leilao):
    assert context['leilao'].nome == nome_leilao
    sistema_limpo.finalizar_leilao(context['leilao'].id, datetime.now() + timedelta(hours=2))

@then(parsers.parse('o vencedor do leilão "{nome_leilao}" deve ser "{nome_vencedor}"'))
def verificar_vencedor(sistema_limpo, context, nome_leilao, nome_vencedor):
    leilao_finalizado = sistema_limpo.encontrar_leilao_por_id(context['leilao'].id)
    vencedor_real = leilao_finalizado.identificar_vencedor()
    
    assert vencedor_real is not None, "Não foi encontrado um vencedor para o leilão."
    assert vencedor_real.participante.nome == nome_vencedor

@then(parsers.parse('o valor do lance vencedor deve ser {valor:f}'))
def verificar_valor_lance(sistema_limpo, context, valor):
    leilao_finalizado = sistema_limpo.encontrar_leilao_por_id(context['leilao'].id)
    vencedor_real = leilao_finalizado.identificar_vencedor()

    assert vencedor_real.valor == valor
