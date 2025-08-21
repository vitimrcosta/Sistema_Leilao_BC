import pytest
from datetime import datetime, timedelta
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

# === FIXTURES (usadas para reaproveitar objetos entre os testes) ===

@pytest.fixture
# Cria um leilão com data de início no passado (estado INATIVO por padrão)
def leilao_inativo():
    agora = datetime.now()
    return Leilao("TV", 1000.0, agora - timedelta(days=1), agora + timedelta(days=2))

@pytest.fixture
# Cria e abre um leilão com data atual (estado ABERTO)
def leilao_aberto(sistema_limpo):
    agora = datetime.now()
    leilao = Leilao("Notebook", 2000.0, agora, agora + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    sistema_limpo.abrir_leilao(leilao.id, agora) # Abre o leilão manualmente
    return leilao

# --- Testes de Filtros ---

# Testes para filtro por range de datas
def test_filtro_por_range_de_datas(sistema_limpo):
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

    sistema_limpo.adicionar_leilao(leilao1)
    sistema_limpo.adicionar_leilao(leilao2)
    sistema_limpo.adicionar_leilao(leilao3)

    # Testa filtro por range completo
    resultados = sistema_limpo.listar_leiloes(
        data_inicio=agora - timedelta(days=3),
        data_fim=agora + timedelta(days=3))
    
    assert len(resultados) == 1
    assert resultados[0].nome == "Leilão Atual"

def test_filtro_por_range_invalido(sistema_limpo):
    """Testa se rejeita corretamente datas invertidas"""
    agora = datetime.now()
    
    # Adiciona um leilão qualquer para garantir que há dados
    leilao_valido = Leilao(
        "Item Válido", 
        1000.0, 
        agora - timedelta(days=1),
        agora + timedelta(days=1)
    )
    sistema_limpo.adicionar_leilao(leilao_valido)
    
    # Testa com datas invertidas (deve levantar exceção)
    with pytest.raises(ValueError, match="Data de início não pode ser maior que data de término"):
        sistema_limpo.listar_leiloes(
            data_inicio=agora + timedelta(days=1),  # Data início > data fim
            data_fim=agora - timedelta(days=1)
        )

def test_filtro_por_estado_e_range(sistema_limpo):
    agora = datetime.now()
    
    # Leilão 1: ABERTO dentro do range
    leilao1 = Leilao("TV", 1000.0, 
                    agora - timedelta(days=2),
                    agora + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao1)
    sistema_limpo.abrir_leilao(leilao1.id, agora - timedelta(days=1))
    
    # Leilão 2: Já FINALIZADO fora do range
    leilao2 = Leilao("Notebook", 2000.0,
                    agora - timedelta(days=5),
                    agora - timedelta(days=3))
    
    sistema_limpo.adicionar_leilao(leilao2)
    sistema_limpo.abrir_leilao(leilao2.id, agora - timedelta(days=4))  # Primeiro abre
    sistema_limpo.finalizar_leilao(leilao2.id, agora - timedelta(days=2))  # Depois finaliza
    
    # Filtra por estado ABERTO e range atual
    resultados = sistema_limpo.listar_leiloes(estado=EstadoLeilao.ABERTO, data_inicio=agora - timedelta(days=3), data_fim=agora + timedelta(days=2))
    
    assert len(resultados) == 1
    assert resultados[0].nome == "TV"

# Mantém os testes existentes (com pequenos ajustes)
def test_filtro_por_data_inicio(sistema_limpo):
    agora = datetime.now()
    leilao1 = Leilao("Item 1", 500.0, agora - timedelta(days=2), agora - timedelta(days=1))
    
    leilao2 = Leilao("Item 2", 600.0, agora, agora + timedelta(days=1))
    
    sistema_limpo.adicionar_leilao(leilao1)
    sistema_limpo.adicionar_leilao(leilao2)
    
    resultados = sistema_limpo.listar_leiloes(data_inicio=agora - timedelta(days=1))
    
    assert len(resultados) == 1
    assert resultados[0].nome == "Item 2"

def test_filtro_apenas_por_data_fim(sistema_limpo):
    """Testa filtro usando apenas data_fim (sem data_inicio)"""
    agora = datetime.now()
    
    # Cria 3 leilões com diferentes datas de término
    leilao_antigo = Leilao("Leilão Antigo", 500.0, 
                          agora - timedelta(days=10), 
                          agora - timedelta(days=5))  # Já terminou
    
    leilao_atual = Leilao("Leilão Atual", 1000.0,
                         agora - timedelta(days=2),
                         agora + timedelta(days=2))   # Ainda em andamento
    
    leilao_futuro = Leilao("Leilão Futuro", 1500.0,
                          agora + timedelta(days=5),
                          agora + timedelta(days=10)) # Só termina no futuro

    sistema_limpo.adicionar_leilao(leilao_antigo)
    sistema_limpo.adicionar_leilao(leilao_atual)
    sistema_limpo.adicionar_leilao(leilao_futuro)

    # Filtra apenas por data_fim (leilões que terminaram até agora)
    resultados = sistema_limpo.listar_leiloes(data_fim=agora)
    
    # Verifica resultados
    assert len(resultados) == 1
    assert resultados[0].nome == "Leilão Antigo"

def test_filtro_data_fim_igual(sistema_limpo):
    agora = datetime.now()
    leilao = Leilao("Leilão Pontual", 1000.0, 
                   agora - timedelta(days=1),
                   agora)  # Termina exatamente agora
    
    sistema_limpo.adicionar_leilao(leilao)
    
    resultados = sistema_limpo.listar_leiloes(data_fim=agora)
    assert len(resultados) == 1  # Deve incluir o leilão que termina exatamente na data fim

# Testes de Filtro
def test_filtro_por_estado(sistema_limpo, leilao_inativo, leilao_aberto):
    # Adiciona os dois leilões ao gerenciador
    sistema_limpo.adicionar_leilao(leilao_inativo)
    
    # Teste filtro por estado ABERTO
    leiloes_abertos = sistema_limpo.listar_leiloes(estado=EstadoLeilao.ABERTO)
    assert len(leiloes_abertos) == 1 # Deve retornar apenas 1
    assert leiloes_abertos[0].nome == "Notebook" # Nome confere com o leilão aberto

    # Teste filtro por estado INATIVO
    leiloes_inativos = sistema_limpo.listar_leiloes(estado=EstadoLeilao.INATIVO)
    assert len(leiloes_inativos) == 1
    assert leiloes_inativos[0].nome == "TV"

def test_filtro_por_data(sistema_limpo):
    # Cria um leilão antigo (não será listado)
    agora = datetime.now()
    leilao1 = Leilao("Item 1", 500.0, agora - timedelta(days=2), agora - timedelta(days=1))
    # Cria um leilão que começa agora (deve ser listado)
    leilao2 = Leilao("Item 2", 600.0, agora, agora + timedelta(days=1))
    
    # Adiciona os dois ao sistema
    sistema_limpo.adicionar_leilao(leilao1)
    sistema_limpo.adicionar_leilao(leilao2)
    
    # Filtra por data de início (somente os que começam depois de ontem)
    resultados = sistema_limpo.listar_leiloes(data_inicio=agora - timedelta(days=1))
    assert len(resultados) == 1 # Apenas 1 resultado esperado
    assert resultados[0].nome == "Item 2"

# --- Testes de Edição Leilao ---

# Testes de Edição
def test_edicao_leilao_inativo(sistema_limpo, leilao_inativo):
    # Adiciona o leilão
    sistema_limpo.adicionar_leilao(leilao_inativo)
    
    # Edita nome e lance mínimo
    sistema_limpo.editar_leilao(leilao_inativo.id, novo_nome="TV 4K", novo_lance_minimo=1200.0)
    
    leilao_editado = sistema_limpo.encontrar_leilao_por_id(leilao_inativo.id)
    assert leilao_editado.nome == "TV 4K"
    assert leilao_editado.lance_minimo == 1200.0
    assert leilao_editado.estado == EstadoLeilao.INATIVO

def test_edicao_parcial_leilao(sistema_limpo, leilao_inativo):
    sistema_limpo.adicionar_leilao(leilao_inativo)
    
    # Edita apenas o nome do leilão
    sistema_limpo.editar_leilao(leilao_inativo.id, novo_nome="TV LED")
    
    # Verifica o novo nome e que o valor do lance mínimo permaneceu
    leilao_editado = sistema_limpo.encontrar_leilao_por_id(leilao_inativo.id)
    assert leilao_editado.nome == "TV LED"
    assert leilao_editado.lance_minimo == 1000.0  # Mantém o valor original

def test_edicao_leilao_aberto_falha(sistema_limpo, leilao_aberto):
    # Tenta editar leilão aberto (não permitido)
    with pytest.raises(ValueError, match="Só é possível editar leilões INATIVOS"):
        sistema_limpo.editar_leilao(leilao_aberto.id, novo_nome="Notebook Gamer")

# --- Testes de Remoção Leilao ---

def test_remocao_leilao_com_lances(sistema_limpo):
    """Testa que não pode remover leilão com lances, mesmo após finalizado"""
    agora = datetime.now()
    
    # 1. Cria leilão que pode ser aberto agora
    leilao = Leilao("TV", 1000.0, agora - timedelta(hours=1), agora + timedelta(hours=2))
    sistema_limpo.adicionar_leilao(leilao)
    
    # 2. Abre o leilão
    sistema_limpo.abrir_leilao(leilao.id, agora)
    
    # 3. Adiciona lance
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    sistema_limpo.adicionar_participante(participante)
    sistema_limpo.adicionar_lance(leilao.id, Lance(1100.0, participante.id, leilao.id, agora))
    
    # 4. Finaliza o leilão (com lances -> estado FINALIZADO)
    sistema_limpo.finalizar_leilao(leilao.id, agora + timedelta(hours=3))
    
    # 5. Tenta remover - deve falhar por ter lances
    with pytest.raises(ValueError, match="Não é possível excluir leilões com lances registrados"):
        sistema_limpo.remover_leilao(leilao.id)
        
def test_remocao_leilao_inativo_com_lances(sistema_limpo):
    """Testa exclusão de leilão inativo COM lances (deve falhar)"""
    agora = datetime.now()
    leilao = Leilao("TV", 1000.0, agora - timedelta(days=1), agora + timedelta(days=2))
    sistema_limpo.adicionar_leilao(leilao)
    
    # Adiciona lance diretamente (sem abrir) - simula caso especial
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    sistema_limpo.adicionar_participante(participante)
    sistema_limpo.abrir_leilao(leilao.id, agora)
    sistema_limpo.adicionar_lance(leilao.id, Lance(1100.0, participante.id, leilao.id, agora))
    sistema_limpo.finalizar_leilao(leilao.id, agora + timedelta(days=3))
    
    with pytest.raises(ValueError, match="Não é possível excluir leilões com lances"):
        sistema_limpo.remover_leilao(leilao.id)

def test_remocao_leilao_aberto_sem_lances(sistema_limpo):
    """Testa que não pode remover leilão ABERTO mesmo sem lances"""
    agora = datetime.now()
    
    # Cria um leilão ABERTO sem lances
    leilao = Leilao("TV Nova", 1500.0, agora - timedelta(hours=1), agora + timedelta(hours=2))
    sistema_limpo.adicionar_leilao(leilao)
    sistema_limpo.abrir_leilao(leilao.id, agora)  # Garante estado ABERTO
    
    # Verifica que o estado está realmente ABERTO
    leilao_aberto = sistema_limpo.encontrar_leilao_por_id(leilao.id)
    assert leilao_aberto.estado == EstadoLeilao.ABERTO
    assert len(leilao_aberto.lances) == 0  # Sem lances
    
    # Tenta remover (deve falhar)
    with pytest.raises(ValueError, match="Não é possível excluir leilões ABERTOS"):
        sistema_limpo.remover_leilao(leilao.id)
    
    # Confirma que o leilão não foi removido
    assert sistema_limpo.encontrar_leilao_por_id(leilao.id) is not None

def test_remocao_leilao_inativo_sem_lances(sistema_limpo, leilao_inativo):
    """Testa remoção bem-sucedida de leilão INATIVO sem lances"""
    # Adiciona o leilão ao gerenciador
    sistema_limpo.adicionar_leilao(leilao_inativo)
    
    # Verifica estado inicial
    assert len(sistema_limpo.listar_leiloes()) == 1
    
    # Remove o leilão
    sistema_limpo.remover_leilao(leilao_inativo.id)
    
    # Verifica se foi removido
    assert len(sistema_limpo.listar_leiloes()) == 0
    assert sistema_limpo.encontrar_leilao_por_id(leilao_inativo.id) is None

def test_remocao_leilao_finalizado_sem_lances(sistema_limpo):
    """Testa remoção de leilão FINALIZADO sem lances (deve ser permitido)"""
    agora = datetime.now()
    leilao = Leilao("TV", 1000.0, agora - timedelta(days=1), agora + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    
    # Abre e finaliza sem adicionar lances (estado EXPIRADO)
    sistema_limpo.abrir_leilao(leilao.id, agora)
    sistema_limpo.finalizar_leilao(leilao.id, agora + timedelta(days=2))
    
    sistema_limpo.remover_leilao(leilao.id)
    
    assert sistema_limpo.encontrar_leilao_por_id(leilao.id) is None

# --- Testes de Remocao de participantes ---

def test_remover_participante_sem_lances(sistema_limpo):
    """Testa remoção de participante que não fez lances"""
    participante = Participante("123.456.789-00", "João", "victor.rcosta@outlook.com", datetime(1990, 1, 1))
    sistema_limpo.adicionar_participante(participante)
    
    # Adiciona um leilão sem lances do participante
    leilao = Leilao("TV", 1000.0, datetime.now(), datetime.now() + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    
    # Remove o participante (deve funcionar)
    sistema_limpo.remover_participante(participante)
    assert sistema_limpo.encontrar_participante_por_cpf(participante.cpf) is None

def test_remover_participante_com_lances(sistema_limpo):
    """Testa tentativa de remover participante que fez lances"""
    participante = Participante("123.456.789-00", "João", "victor.rcosta@outlook.com", datetime(1990, 1, 1))
    sistema_limpo.adicionar_participante(participante)
    
    # Cria e adiciona um leilão
    agora = datetime.now()
    leilao = Leilao("TV", 1000.0, agora, agora + timedelta(days=1))
    sistema_limpo.adicionar_leilao(leilao)
    sistema_limpo.abrir_leilao(leilao.id, agora)
    
    # Adiciona um lance do participante
    sistema_limpo.adicionar_lance(leilao.id, Lance(1100.0, participante.id, leilao.id, agora))
    
    # Tenta remover (deve falhar)
    with pytest.raises(ValueError, match="Participante não pode ser removido"):
        sistema_limpo.remover_participante(participante)
    
    # Verifica que o participante ainda está na lista
    assert sistema_limpo.encontrar_participante_por_cpf(participante.cpf) is not None

# --- Testes Encontrar Leilao por ID ---

def test_encontrar_leilao_por_id_inexistente(sistema_limpo):
    """Testa busca por ID de leilão que não existe (versão simples)"""
    # Usa um ID arbitrário que não existe
    assert sistema_limpo.encontrar_leilao_por_id(999999) is None