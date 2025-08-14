import pytest
from datetime import datetime, timedelta
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante


def test_lance_repr():
    lance = Lance(100.0, 1, 1, datetime.now())
    lance.id = 1
    assert repr(lance) == "<Lance(id=1, valor=100.0, participante_id=1, leilao_id=1)>"

def test_leilao_repr():
    leilao = Leilao("Teste", 100.0, datetime.now(), datetime.now() + timedelta(days=1))
    leilao.id = 1
    assert repr(leilao) == f"<Leilao(id=1, nome='Teste', estado={EstadoLeilao.INATIVO.name})>"

def test_participante_repr():
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    participante.id = 1
    assert repr(participante) == "<Participante(id=1, nome='João', cpf='123.456.789-00')>"

def test_participante_str():
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    assert str(participante) == "Participante: João (123.456.789-00)"

def test_participante_eq():
    p1 = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    p2 = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    p3 = Participante("111.222.333-44", "Maria", "maria@email.com", datetime(1985, 5, 15))
    assert p1 == p2
    assert p1 != p3
    assert p1 != "123.456.789-00"