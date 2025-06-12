import pytest
from datetime import datetime, timedelta
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

# Fixture que cria um participante para usar nos testes
@pytest.fixture
def participante():
    return Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))

# Fixture que cria um leilão válido para usar nos testes
@pytest.fixture
def leilao_valido():
    agora = datetime.now()
    return Leilao("Item Teste", 500.0, agora, agora + timedelta(days=1))

# Testa se ao criar um leilão, o estado inicial é INATIVO
# --- Testes Básicos ---
def test_leilao_criado_com_estado_inativo():
    leilao = Leilao("PS5", 1000.0, datetime.now(), datetime.now() + timedelta(days=1))
    assert leilao.estado == EstadoLeilao.INATIVO, "Leilão deve iniciar como INATIVO"

# Testa se a data de término do leilão é posterior à data de início, senão lança erro
def test_validacao_datas_leilao():
    with pytest.raises(ValueError, match="Data de término deve ser posterior"):
        Leilao("Item", 100.0, datetime.now(), datetime.now() - timedelta(days=1))

# Testa se abrir um leilão antes da data de início lança erro
# --- Testes de Abertura ---
def test_abrir_leilao_fora_da_data_falha(leilao_valido):
    with pytest.raises(ValueError, match="antes da data de início"):
        leilao_valido.abrir(datetime.now() - timedelta(days=1))

# Testa se tentar abrir um leilão já aberto lança erro
def test_abrir_leilao_ja_aberto(leilao_valido):
    leilao_valido.abrir(datetime.now())
    with pytest.raises(ValueError, match="só pode ser aberto se estiver INATIVO"):
        leilao_valido.abrir(datetime.now())

# --- Testes de Finalização ---

# Testa se um leilão sem lances, quando finalizado, fica com estado EXPIRADO
def test_finalizar_leilao_sem_lances(leilao_valido):
    leilao_valido.abrir(datetime.now())
    leilao_valido.finalizar(datetime.now() + timedelta(days=2))
    assert leilao_valido.estado == EstadoLeilao.EXPIRADO, "Leilão sem lances deve expirar"

# Testa se tentar finalizar um leilão antes da data de término lança erro
def test_finalizar_leilao_antes_da_data(leilao_valido):
    leilao_valido.abrir(datetime.now())
    with pytest.raises(ValueError, match="antes da data de término"):
        leilao_valido.finalizar(datetime.now())

def test_finalizar_leilao_com_lances(leilao_valido, participante):
    """Testa se leilão com lances vai para estado FINALIZADO"""
    leilao_valido.abrir(datetime.now())
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    
    # Finaliza após data término (EXIGÊNCIA TESTADA)
    leilao_valido.finalizar(datetime.now() + timedelta(days=2))
    
    assert leilao_valido.estado == EstadoLeilao.FINALIZADO

def test_estado_pos_finalizacao(leilao_valido, participante):
    """Testa o fluxo completo: INATIVO -> ABERTO -> FINALIZADO"""
    leilao_valido.abrir(datetime.now())
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    leilao_valido.finalizar(datetime.now() + timedelta(days=1))
    
    # Verifica o estado final (EXIGÊNCIA INDIRETA)
    assert leilao_valido.estado == EstadoLeilao.FINALIZADO
    assert leilao_valido.identificar_vencedor().participante == participante

# --- Testes de Lances ---

# Testa se adicionar lance quando o leilão está fechado (não aberto) lança erro
def test_adicionar_lance_em_leilao_fechado(leilao_valido, participante):
    lance = Lance(600.0, participante, leilao_valido, datetime.now())
    with pytest.raises(ValueError, match="deve estar ABERTO"):
        leilao_valido.adicionar_lance(lance)

# Testa se adicionar lance menor que o lance mínimo do leilão lança erro
def test_lance_menor_que_minimo(leilao_valido, participante):
    leilao_valido.abrir(datetime.now())
    lance = Lance(400.0, participante, leilao_valido, datetime.now())
    with pytest.raises(ValueError, match=r"Lance deve ser ≥ R\$500\.00"):
        leilao_valido.adicionar_lance(lance)

# --- Testes de Vencedor ---

# Testa se tentar identificar o vencedor antes do leilão ser finalizado lança erro
def test_identificar_vencedor_antes_de_finalizar(leilao_valido):
    with pytest.raises(ValueError, match="não finalizado"):
        leilao_valido.identificar_vencedor()

# Fixture que cria uma lista de participantes para testes de lance
@pytest.fixture
def participantes():
    return [
        Participante("111.222.333-44", "João", "joao@email.com", datetime(1990, 1, 1)),
        Participante("555.666.777-88", "Maria", "maria@email.com", datetime(1985, 5, 15))
    ]

# Testa se as propriedades maior_lance e menor_lance retornam os valores corretos
def test_propriedades_maior_menor_lance(leilao_valido, participantes):
    leilao_valido.abrir(datetime.now())
    leilao_valido.adicionar_lance(Lance(600.0, participantes[0], leilao_valido, datetime.now()))
    leilao_valido.adicionar_lance(Lance(800.0, participantes[1], leilao_valido, datetime.now()))
    
    assert leilao_valido.maior_lance == 800.0
    assert leilao_valido.menor_lance == 600.0

def test_finalizar_leilao_inativo(leilao_valido):
    """Testa que não pode finalizar leilão INATIVO"""
    with pytest.raises(ValueError, match="só pode ser finalizado se estiver ABERTO"):
        leilao_valido.finalizar(datetime.now() + timedelta(days=2))

def test_finalizar_leilao_ja_finalizado(leilao_valido, participante):
    """Testa que não pode finalizar leilão já FINALIZADO"""
    # 1. Abre o leilão
    leilao_valido.abrir(datetime.now())
    
    # 2. Adiciona lance e finaliza
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    leilao_valido.finalizar(datetime.now() + timedelta(days=2), enviar_email=False)
    
    # 3. Tenta finalizar novamente
    with pytest.raises(ValueError, match="só pode ser finalizado se estiver ABERTO"):
        leilao_valido.finalizar(datetime.now() + timedelta(days=3))

def test_finalizar_leilao_expirado(leilao_valido):
    """Testa que não pode finalizar leilão EXPIRADO"""
    # 1. Abre e finaliza sem lances (expira)
    leilao_valido.abrir(datetime.now())
    leilao_valido.finalizar(datetime.now() + timedelta(days=2))
    
    # 2. Tenta finalizar novamente
    with pytest.raises(ValueError, match="só pode ser finalizado se estiver ABERTO"):
        leilao_valido.finalizar(datetime.now() + timedelta(days=3))

def test_lance_igual_ao_ultimo(leilao_valido, participante):
    """Testa que não pode adicionar lance igual ao último"""
    leilao_valido.abrir(datetime.now())
    
    # Primeiro lance válido
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    
    # Tenta adicionar lance com mesmo valor
    with pytest.raises(ValueError) as exc_info:
        leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    
    # Verifica mensagem exata
    assert "Lance deve ser > R$600.00" in str(exc_info.value)

def test_lance_menor_que_ultimo(leilao_valido, participantes):
    """Testa que não pode adicionar lance menor que o último"""
    leilao_valido.abrir(datetime.now())
    
    # Primeiro lance válido
    leilao_valido.adicionar_lance(Lance(1000.0, participantes[0], leilao_valido, datetime.now()))
    
    # Tenta adicionar lance menor
    with pytest.raises(ValueError) as exc_info:
        leilao_valido.adicionar_lance(Lance(800.0, participantes[1], leilao_valido, datetime.now()))
    
    # Verifica mensagem exata
    assert "Lance deve ser > R$1000.00" in str(exc_info.value)

def test_lances_validos_em_sequencia(leilao_valido, participantes):
    """Testa sequência válida de lances crescentes"""
    leilao_valido.abrir(datetime.now())
    
    # Lances em ordem crescente
    valores = [600.0, 700.0, 800.0]
    for i, valor in enumerate(valores):
        leilao_valido.adicionar_lance(Lance(valor, participantes[i % 2], leilao_valido, datetime.now()))
    
    assert len(leilao_valido.lances) == 3
    assert leilao_valido.maior_lance == 800.0

def test_lances_consecutivos_mesmo_participante(leilao_valido, participante):
    """Testa que um participante não pode dar dois lances seguidos"""
    leilao_valido.abrir(datetime.now())
    
    # Primeiro lance válido
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    
    # Tenta adicionar segundo lance do mesmo participante
    with pytest.raises(ValueError) as exc_info:
        leilao_valido.adicionar_lance(Lance(700.0, participante, leilao_valido, datetime.now()))
    
    # Verifica mensagem exata de erro
    assert "Participante não pode dar lances consecutivos" in str(exc_info.value)
    assert len(leilao_valido.lances) == 1  # Confirma que o segundo lance não foi adicionado

def test_lances_alternados_participantes_diferentes(leilao_valido, participantes):
    """Testa que participantes diferentes podem dar lances alternados"""
    leilao_valido.abrir(datetime.now())
    
    # Primeiro participante
    leilao_valido.adicionar_lance(Lance(600.0, participantes[0], leilao_valido, datetime.now()))
    
    # Segundo participante
    leilao_valido.adicionar_lance(Lance(700.0, participantes[1], leilao_valido, datetime.now()))
    
    # Primeiro participante novamente
    leilao_valido.adicionar_lance(Lance(800.0, participantes[0], leilao_valido, datetime.now()))
    
    assert len(leilao_valido.lances) == 3  # Todos os lances foram aceitos

def test_identificar_vencedor_com_multiplos_lances(leilao_valido, participantes):
    """Testa identificação do vencedor com múltiplos lances"""
    # 1. Abre o leilão
    leilao_valido.abrir(datetime.now())
    
    # 2. Adiciona lances em ORDEM CRESCENTE de valores
    leilao_valido.adicionar_lance(Lance(600.0, participantes[0], leilao_valido, datetime.now()))
    leilao_valido.adicionar_lance(Lance(700.0, participantes[1], leilao_valido, datetime.now()))
    leilao_valido.adicionar_lance(Lance(800.0, participantes[0], leilao_valido, datetime.now()))
    
    # 3. Finaliza o leilão (sem enviar e-mail)
    leilao_valido.finalizar(datetime.now() + timedelta(days=1), enviar_email=False)
    
    # 4. Identifica o vencedor
    vencedor = leilao_valido.identificar_vencedor()
    
    # 5. Verifica o resultado
    assert vencedor.valor == 800.0  # Maior lance
    assert vencedor.participante == participantes[0]  # Participante correto

def test_identificar_vencedor_com_unico_lance(leilao_valido, participante):
    """Testa identificação do vencedor quando há apenas um lance"""
    leilao_valido.abrir(datetime.now())
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    leilao_valido.finalizar(datetime.now() + timedelta(days=1), enviar_email=False)
    
    vencedor = leilao_valido.identificar_vencedor()
    assert vencedor.valor == 600.0
    assert vencedor.participante == participante

def test_identificar_vencedor_com_lances_iguais(leilao_valido, participantes):
    """Testa comportamento quando há um único lance máximo"""
    leilao_valido.abrir(datetime.now())
    
    # Adiciona lances com valores crescentes
    leilao_valido.adicionar_lance(Lance(900.0, participantes[0], leilao_valido, datetime.now()))
    leilao_valido.adicionar_lance(Lance(1000.0, participantes[1], leilao_valido, datetime.now()))
    
    leilao_valido.finalizar(datetime.now() + timedelta(days=1), enviar_email=False)
    
    vencedor = leilao_valido.identificar_vencedor()
    assert vencedor.valor == 1000.0
    assert vencedor.participante == participantes[1]  # Último participante com lance máximo

def test_listar_lances_ordenados_com_multiplos_lances(leilao_valido, participantes):
    """Testa ordenação com múltiplos lances em ordem crescente"""
    leilao_valido.abrir(datetime.now())
    
    # Adiciona lances em ORDEM CRESCENTE para respeitar as regras
    leilao_valido.adicionar_lance(Lance(500.0, participantes[0], leilao_valido, datetime.now()))
    leilao_valido.adicionar_lance(Lance(750.0, participantes[1], leilao_valido, datetime.now()))
    leilao_valido.adicionar_lance(Lance(1000.0, participantes[0], leilao_valido, datetime.now()))
    
    lances_ordenados = leilao_valido.listar_lances_ordenados()
    
    # Verifica ordem e valores
    assert len(lances_ordenados) == 3
    assert lances_ordenados[0].valor == 500.0
    assert lances_ordenados[1].valor == 750.0
    assert lances_ordenados[2].valor == 1000.0
    assert lances_ordenados[0].participante == participantes[0]

def test_listar_lances_ordenados_com_unico_lance(leilao_valido, participante):
    """Testa ordenação com apenas um lance"""
    leilao_valido.abrir(datetime.now())
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    
    lances_ordenados = leilao_valido.listar_lances_ordenados()
    
    assert len(lances_ordenados) == 1
    assert lances_ordenados[0].valor == 600.0

def test_str_leilao_finalizado_com_vencedor(leilao_valido, participante):
    """Testa representação textual de leilão finalizado com vencedor"""
    # 1. Abre o leilão
    leilao_valido.abrir(datetime.now())
    
    # 2. Adiciona lance
    leilao_valido.adicionar_lance(Lance(600.0, participante, leilao_valido, datetime.now()))
    
    # 3. Finaliza o leilão
    leilao_valido.finalizar(datetime.now() + timedelta(days=1), enviar_email=False)
    
    # 4. Verifica a representação textual
    resultado = str(leilao_valido)
    assert "Leilão: Item Teste (FINALIZADO)" in resultado
    assert "Vencedor: João" in resultado  # Nome do participante da fixture

def test_str_leilao_em_outros_estados(leilao_valido):
    """Testa representação textual em estados não finalizados"""
    # Estado INATIVO (padrão)
    assert str(leilao_valido) == "Leilão: Item Teste (INATIVO)"
    
    # Estado ABERTO
    leilao_valido.abrir(datetime.now())
    assert str(leilao_valido) == "Leilão: Item Teste (ABERTO)"
    
    # Estado EXPIRADO (sem lances)
    leilao_valido.finalizar(datetime.now() + timedelta(days=1), enviar_email=False)
    assert str(leilao_valido) == "Leilão: Item Teste (EXPIRADO)"