import pytest
from datetime import datetime, timedelta  # Deve estar assim
from models.leilao import Leilao, EstadoLeilao

def test_leilao_criado_com_estado_inativo():
    agora = datetime.now()
    leilao = Leilao("Playstation 5", 1000.0, agora + timedelta(days=1), agora + timedelta(days=2))
    assert leilao.estado == EstadoLeilao.INATIVO

def test_abrir_leilao_fora_da_data_falha():
    agora = datetime.now()
    leilao = Leilao("Xbox Series X", 500.0, agora + timedelta(days=1), agora + timedelta(days=2))
    with pytest.raises(ValueError):
        leilao.abrir(agora)  # Tenta abrir antes da data de início

def test_leilao_finalizado_sem_lances_vira_expirado():
    agora = datetime.now()
    leilao = Leilao("Notebook Gamer", 2000.0, agora - timedelta(days=2), agora - timedelta(days=1))
    leilao.abrir(agora - timedelta(days=1))  # Abre no passado (simulação)
    leilao.finalizar(agora)
    assert leilao.estado == EstadoLeilao.EXPIRADO
