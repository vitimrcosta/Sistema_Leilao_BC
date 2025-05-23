import pytest
from datetime import datetime, timedelta
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

@pytest.fixture
def gerenciador():
    return GerenciadorLeiloes()

@pytest.fixture
def leilao_inativo():
    agora = datetime.now()
    # Data de início no passado para permitir abertura imediata
    return Leilao("TV", 1000.0, agora - timedelta(days=1), agora + timedelta(days=2))

@pytest.fixture
def leilao_aberto():
    agora = datetime.now()
    leilao = Leilao("Notebook", 2000.0, agora, agora + timedelta(days=1))
    leilao.abrir(agora)
    return leilao

# Testes de Filtro
def test_filtro_por_estado(gerenciador, leilao_inativo, leilao_aberto):
    gerenciador.adicionar_leilao(leilao_inativo)
    gerenciador.adicionar_leilao(leilao_aberto)
    
    # Teste filtro por estado ABERTO
    leiloes_abertos = gerenciador.listar_leiloes(estado=EstadoLeilao.ABERTO)
    assert len(leiloes_abertos) == 1
    assert leiloes_abertos[0].nome == "Notebook"
    
    # Teste filtro por estado INATIVO
    leiloes_inativos = gerenciador.listar_leiloes(estado=EstadoLeilao.INATIVO)
    assert len(leiloes_inativos) == 1
    assert leiloes_inativos[0].nome == "TV"

def test_filtro_por_data(gerenciador):
    agora = datetime.now()
    leilao1 = Leilao("Item 1", 500.0, agora - timedelta(days=2), agora - timedelta(days=1))
    leilao2 = Leilao("Item 2", 600.0, agora, agora + timedelta(days=1))
    
    gerenciador.adicionar_leilao(leilao1)
    gerenciador.adicionar_leilao(leilao2)
    
    # Filtro por data de início
    resultados = gerenciador.listar_leiloes(data_inicio=agora - timedelta(days=1))
    assert len(resultados) == 1
    assert resultados[0].nome == "Item 2"

# Testes de Edição
def test_edicao_leilao_inativo(gerenciador, leilao_inativo):
    gerenciador.adicionar_leilao(leilao_inativo)
    
    # Edita nome e lance mínimo
    gerenciador.editar_leilao(id(leilao_inativo), novo_nome="TV 4K", novo_lance_minimo=1200.0)
    
    assert leilao_inativo.nome == "TV 4K"
    assert leilao_inativo.lance_minimo == 1200.0
    assert leilao_inativo.estado == EstadoLeilao.INATIVO

def test_edicao_parcial_leilao(gerenciador, leilao_inativo):
    gerenciador.adicionar_leilao(leilao_inativo)
    
    # Edita apenas o nome
    gerenciador.editar_leilao(id(leilao_inativo), novo_nome="TV LED")
    
    assert leilao_inativo.nome == "TV LED"
    assert leilao_inativo.lance_minimo == 1000.0  # Mantém o valor original

def test_edicao_leilao_aberto_falha(gerenciador, leilao_aberto):
    gerenciador.adicionar_leilao(leilao_aberto)
    
    with pytest.raises(ValueError, match="Só é possível editar leilões INATIVOS"):
        gerenciador.editar_leilao(id(leilao_aberto), novo_nome="Notebook Gamer")

def test_remocao_leilao_com_lances(gerenciador):
    """Testa que não pode remover leilão com lances, mesmo após finalizado"""
    agora = datetime.now()
    
    # 1. Cria leilão que pode ser aberto agora
    leilao = Leilao("TV", 1000.0, agora - timedelta(hours=1), agora + timedelta(hours=2))
    
    # 2. Abre o leilão
    leilao.abrir(agora)
    
    # 3. Adiciona lance
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    leilao.adicionar_lance(Lance(1100.0, participante, leilao, agora))
    
    # 4. Finaliza o leilão (com lances -> estado FINALIZADO)
    leilao.finalizar(agora + timedelta(hours=3), enviar_email=False)
    
    gerenciador.adicionar_leilao(leilao)
    
    # 5. Tenta remover - deve falhar por ter lances
    with pytest.raises(ValueError, match="Não é possível excluir leilões com lances registrados"):
        gerenciador.remover_leilao(id(leilao))
        
def test_remocao_leilao_inativo_com_lances(gerenciador):
    """Testa exclusão de leilão inativo COM lances (deve falhar)"""
    agora = datetime.now()
    leilao = Leilao("TV", 1000.0, agora + timedelta(days=1), agora + timedelta(days=2))
    
    # Adiciona lance diretamente (sem abrir) - simula caso especial
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    leilao.lances.append(Lance(1100.0, participante, leilao, agora))  # Adição direta
    
    gerenciador.adicionar_leilao(leilao)
    
    with pytest.raises(ValueError, match="Não é possível excluir leilões com lances"):
        gerenciador.remover_leilao(id(leilao))


def test_remocao_leilao_sem_lances(gerenciador, leilao_inativo):
    """Testa que pode remover leilão inativo SEM lances"""
    gerenciador.adicionar_leilao(leilao_inativo)
    gerenciador.remover_leilao(id(leilao_inativo))
    assert len(gerenciador.listar_leiloes()) == 0