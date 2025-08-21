import pytest
from datetime import datetime, timedelta
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante


def test_abrir_leilao_nao_encontrado(sistema_limpo):
    with pytest.raises(ValueError, match="Leilão não encontrado"):
        sistema_limpo.abrir_leilao(999, datetime.now())

def test_finalizar_leilao_nao_encontrado(sistema_limpo):
    with pytest.raises(ValueError, match="Leilão não encontrado"):
        sistema_limpo.finalizar_leilao(999, datetime.now())

def test_adicionar_lance_leilao_nao_encontrado(sistema_limpo):
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    sistema_limpo.adicionar_participante(participante)
    lance = Lance(100.0, participante.id, 999, datetime.now())
    with pytest.raises(ValueError, match="Leilão não encontrado"):
        sistema_limpo.adicionar_lance(999, lance)

def test_editar_leilao_nao_encontrado(sistema_limpo):
    with pytest.raises(ValueError, match="Leilão não encontrado"):
        sistema_limpo.editar_leilao(999, novo_nome="Teste")

def test_remover_leilao_nao_encontrado(sistema_limpo):
    with pytest.raises(ValueError, match="Leilão não encontrado"):
        sistema_limpo.remover_leilao(999)

def test_remover_participante_nao_encontrado(sistema_limpo):
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    with pytest.raises(ValueError, match="Participante não encontrado"):
        sistema_limpo.remover_participante(participante)