import pytest
from datetime import datetime, timedelta
from models.leilao import Leilao
from models.participante import Participante
from models.lance import Lance

def test_lance_valido():
    agora = datetime.now()
    leilao = Leilao("TV 4K", 1000.0, agora - timedelta(days=1), agora + timedelta(days=1))
    leilao.abrir(agora)
    
    participante = Participante("111.222.333-44", "Maria", "maria@email.com", datetime(1985, 10, 20))
    lance = Lance(1500.0, participante, leilao, agora)
    
    leilao.adicionar_lance(lance)

    assert len(leilao.lances) == 1

def test_lance_menor_que_minimo():
    # Arrange
    leilao = Leilao("Celular", 500.0, datetime.now(), datetime.now() + timedelta(days=1))
    leilao.abrir(datetime.now())
    participante = Participante("999.888.777-66", "Carlos", "carlos@email.com", datetime(1995, 3, 12))
    lance_invalido = Lance(300.0, participante, leilao, datetime.now())
    
    # Act/Assert
    with pytest.raises(ValueError) as erro:
        leilao.adicionar_lance(lance_invalido)
    
    # Verifica a mensagem de erro
    assert "Lance deve ser ≥ R$500.00" in str(erro.value)


def test_str_do_lance():
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    leilao = Leilao("TV", 1000.0, datetime.now(), datetime.now() + timedelta(days=1))
    lance = Lance(1500.0, participante, leilao, datetime.now())
    
    assert str(lance) == "Lance de R$1500.00 por João"