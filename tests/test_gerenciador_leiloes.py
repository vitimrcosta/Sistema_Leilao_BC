import pytest
from datetime import datetime, timedelta
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

# === FIXTURES (usadas para reaproveitar objetos entre os testes) ===

@pytest.fixture
# Cria e retorna um novo gerenciador de leilões vazio
def gerenciador():
    return GerenciadorLeiloes()

@pytest.fixture
# Cria um leilão com data de início no passado (estado INATIVO por padrão)
def leilao_inativo():
    agora = datetime.now()
    return Leilao("TV", 1000.0, agora - timedelta(days=1), agora + timedelta(days=2))

@pytest.fixture
# Cria e abre um leilão com data atual (estado ABERTO)
def leilao_aberto():
    agora = datetime.now()
    leilao = Leilao("Notebook", 2000.0, agora, agora + timedelta(days=1))
    leilao.abrir(agora) # Abre o leilão manualmente
    return leilao

# Testes para filtro por range de datas
def test_filtro_por_range_de_datas(gerenciador):
    agora = datetime.now()
    
    # Cria 3 leilões com diferentes intervalos
    leilao1 = Leilao("Leilão Antigo", 500.0, 
                    agora - timedelta(days=10), 
                    agora - timedelta(days=5))
    
    leilao2 = Leilao("Leilão Atual", 1000.0,
                    agora - timedelta(days=2),
                    agora + timedelta(days=2))
    
    leilao3 = Leilao("Leilão Futuro", 1500.0,
                    agora + timedelta(days=5),
                    agora + timedelta(days=10))

    gerenciador.adicionar_leilao(leilao1)
    gerenciador.adicionar_leilao(leilao2)
    gerenciador.adicionar_leilao(leilao3)

    # Testa filtro por range completo
    resultados = gerenciador.listar_leiloes(
        data_inicio=agora - timedelta(days=3),
        data_fim=agora + timedelta(days=3))
    
    assert len(resultados) == 1
    assert resultados[0].nome == "Leilão Atual"

def test_filtro_por_range_invalido(gerenciador):
    """Testa se rejeita corretamente datas invertidas"""
    agora = datetime.now()
    
    # Adiciona um leilão qualquer para garantir que há dados
    leilao_valido = Leilao(
        "Item Válido", 
        1000.0, 
        agora - timedelta(days=1),
        agora + timedelta(days=1)
    )
    gerenciador.adicionar_leilao(leilao_valido)
    
    # Testa com datas invertidas (deve levantar exceção)
    with pytest.raises(ValueError, match="Data de início não pode ser maior que data de término"):
        gerenciador.listar_leiloes(
            data_inicio=agora + timedelta(days=1),  # Data início > data fim
            data_fim=agora - timedelta(days=1)
        )

def test_filtro_por_estado_e_range(gerenciador):
    agora = datetime.now()
    
    # Leilão 1: ABERTO dentro do range
    leilao1 = Leilao("TV", 1000.0, 
                    agora - timedelta(days=2),
                    agora + timedelta(days=1))
    # Abre o leilão corretamente
    leilao1.abrir(agora - timedelta(days=1))
    
    # Leilão 2: Já FINALIZADO fora do range
    leilao2 = Leilao("Notebook", 2000.0,
                    agora - timedelta(days=5),
                    agora - timedelta(days=3))
    # Fluxo completo de estados:
    leilao2.abrir(agora - timedelta(days=4))  # Primeiro abre
    leilao2.finalizar(agora - timedelta(days=2))  # Depois finaliza
    
    gerenciador.adicionar_leilao(leilao1)
    gerenciador.adicionar_leilao(leilao2)

    # Filtra por estado ABERTO e range atual
    resultados = gerenciador.listar_leiloes(estado=EstadoLeilao.ABERTO, data_inicio=agora - timedelta(days=3), data_fim=agora + timedelta(days=2))
    
    assert len(resultados) == 1
    assert resultados[0].nome == "TV"

# Mantém os testes existentes (com pequenos ajustes)
def test_filtro_por_data_inicio(gerenciador):
    agora = datetime.now()
    leilao1 = Leilao("Item 1", 500.0, agora - timedelta(days=2), agora - timedelta(days=1))
    
    leilao2 = Leilao("Item 2", 600.0, agora, agora + timedelta(days=1))
    
    gerenciador.adicionar_leilao(leilao1)
    gerenciador.adicionar_leilao(leilao2)
    
    resultados = gerenciador.listar_leiloes(data_inicio=agora - timedelta(days=1))
    
    assert len(resultados) == 1
    assert resultados[0].nome == "Item 2"

# Testes de Filtro
def test_filtro_por_estado(gerenciador, leilao_inativo, leilao_aberto):
    # Adiciona os dois leilões ao gerenciador
    gerenciador.adicionar_leilao(leilao_inativo)
    gerenciador.adicionar_leilao(leilao_aberto)
    
    # Teste filtro por estado ABERTO
    leiloes_abertos = gerenciador.listar_leiloes(estado=EstadoLeilao.ABERTO)
    assert len(leiloes_abertos) == 1 # Deve retornar apenas 1
    assert leiloes_abertos[0].nome == "Notebook" # Nome confere com o leilão aberto

    # Teste filtro por estado INATIVO
    leiloes_inativos = gerenciador.listar_leiloes(estado=EstadoLeilao.INATIVO)
    assert len(leiloes_inativos) == 1
    assert leiloes_inativos[0].nome == "TV"

def test_filtro_por_data(gerenciador):
    # Cria um leilão antigo (não será listado)
    agora = datetime.now()
    leilao1 = Leilao("Item 1", 500.0, agora - timedelta(days=2), agora - timedelta(days=1))
    # Cria um leilão que começa agora (deve ser listado)
    leilao2 = Leilao("Item 2", 600.0, agora, agora + timedelta(days=1))
    
    # Adiciona os dois ao sistema
    gerenciador.adicionar_leilao(leilao1)
    gerenciador.adicionar_leilao(leilao2)
    
    # Filtra por data de início (somente os que começam depois de ontem)
    resultados = gerenciador.listar_leiloes(data_inicio=agora - timedelta(days=1))
    assert len(resultados) == 1 # Apenas 1 resultado esperado
    assert resultados[0].nome == "Item 2"

# Testes de Edição
def test_edicao_leilao_inativo(gerenciador, leilao_inativo):
    # Adiciona o leilão
    gerenciador.adicionar_leilao(leilao_inativo)
    
    # Edita nome e lance mínimo
    gerenciador.editar_leilao(id(leilao_inativo), novo_nome="TV 4K", novo_lance_minimo=1200.0)
    
    assert leilao_inativo.nome == "TV 4K"
    assert leilao_inativo.lance_minimo == 1200.0
    assert leilao_inativo.estado == EstadoLeilao.INATIVO

def test_edicao_parcial_leilao(gerenciador, leilao_inativo):
    gerenciador.adicionar_leilao(leilao_inativo)
    
    # Edita apenas o nome do leilão
    gerenciador.editar_leilao(id(leilao_inativo), novo_nome="TV LED")
    
    # Verifica o novo nome e que o valor do lance mínimo permaneceu
    assert leilao_inativo.nome == "TV LED"
    assert leilao_inativo.lance_minimo == 1000.0  # Mantém o valor original

def test_edicao_leilao_aberto_falha(gerenciador, leilao_aberto):
    gerenciador.adicionar_leilao(leilao_aberto)
    # Tenta editar leilão aberto (não permitido)
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