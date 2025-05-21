import pytest
from datetime import datetime, timedelta
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.leilao import Leilao, EstadoLeilao

def test_filtro_por_estado():
    gerenciador = GerenciadorLeiloes()
    leilao_aberto = Leilao("TV", 1000.0, datetime.now(), datetime.now() + timedelta(days=1))
    leilao_aberto.abrir(datetime.now())
    
    leilao_inativo = Leilao("Notebook", 2000.0, datetime.now() + timedelta(days=2), datetime.now() + timedelta(days=3))
    
    gerenciador.adicionar_leilao(leilao_aberto)
    gerenciador.adicionar_leilao(leilao_inativo)
    
    leiloes_abertos = gerenciador.listar_leiloes(estado=EstadoLeilao.ABERTO)
    assert len(leiloes_abertos) == 1
    assert leiloes_abertos[0].nome == "TV"