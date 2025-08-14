import pytest
from datetime import datetime, timedelta
from models.leilao import Leilao
from models.participante import Participante
from models.lance import Lance

def test_lance_valido(sistema_limpo):
    agora = datetime.now()
    leilao = Leilao("TV 4K", 1000.0, agora - timedelta(days=1), agora + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    sistema_limpo.abrir_leilao(leilao.id, agora)
    
    participante = Participante("111.222.333-44", "Maria", "maria@email.com", datetime(1985, 10, 20))
    sistema_limpo.adicionar_participante(participante)
    lance = Lance(1500.0, participante.id, leilao.id, agora)
    
    sistema_limpo.adicionar_lance(leilao.id, lance)

    leilao_com_lance = sistema_limpo.encontrar_leilao_por_id(leilao.id)
    assert len(leilao_com_lance.lances) == 1

def test_lance_menor_que_minimo(sistema_limpo):
    # Arrange
    agora = datetime.now()
    leilao = Leilao("Celular", 500.0, agora, agora + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    sistema_limpo.abrir_leilao(leilao.id, agora)
    participante = Participante("999.888.777-66", "Carlos", "carlos@email.com", datetime(1995, 3, 12))
    sistema_limpo.adicionar_participante(participante)
    lance_invalido = Lance(300.0, participante.id, leilao.id, agora)
    
    # Act/Assert
    with pytest.raises(ValueError) as erro:
        sistema_limpo.adicionar_lance(leilao.id, lance_invalido)
    
    # Verifica a mensagem de erro
    assert "Lance deve ser >= R$500.00" in str(erro.value)


def test_str_do_lance(sistema_limpo):
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    sistema_limpo.adicionar_participante(participante)
    leilao = Leilao("TV", 1000.0, datetime.now(), datetime.now() + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    sistema_limpo.abrir_leilao(leilao.id, datetime.now())
    lance = Lance(1500.0, participante.id, leilao.id, datetime.now())
    sistema_limpo.adicionar_lance(leilao.id, lance)
    
    lance_db = sistema_limpo.db.query(Lance).filter(Lance.id == lance.id).first()
    assert str(lance_db) == f"Lance de R$1500.00 por {participante.nome}"