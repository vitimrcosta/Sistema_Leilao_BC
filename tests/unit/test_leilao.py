import pytest
from datetime import datetime, timedelta
from models.lance import Lance
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

# Fixture que cria um participante para usar nos testes
@pytest.fixture
def participante(sistema_limpo):
    p = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    return sistema_limpo.adicionar_participante(p)

# Fixture que cria um leilão válido para usar nos testes
@pytest.fixture
def leilao_valido(sistema_limpo):
    agora = datetime.now()
    leilao = Leilao("Item Teste", 500.0, agora, agora + timedelta(days=1))
    return sistema_limpo.adicionar_leilao(leilao)

# Testa se ao criar um leilão, o estado inicial é INATIVO
# --- Testes Básicos ---
def test_leilao_criado_com_estado_inativo(leilao_valido):
    assert leilao_valido.estado == EstadoLeilao.INATIVO, "Leilão deve iniciar como INATIVO"

# Testa se a data de término do leilão é posterior à data de início, senão lança erro
def test_validacao_datas_leilao():
    with pytest.raises(ValueError, match="Data de término deve ser posterior"):
        Leilao("Item", 100.0, datetime.now(), datetime.now() - timedelta(days=1))

# Testa se abrir um leilão antes da data de início lança erro
# --- Testes de Abertura ---
def test_abrir_leilao_fora_da_data_falha(sistema_limpo, leilao_valido):
    with pytest.raises(ValueError, match="antes da data de início"):
        sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now() - timedelta(days=1))

# Testa se tentar abrir um leilão já aberto lança erro
def test_abrir_leilao_ja_aberto(sistema_limpo, leilao_valido):
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    with pytest.raises(ValueError, match="só pode ser aberto se estiver INATIVO"):
        sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())

# --- Testes de Finalização ---

# Testa se um leilão sem lances, quando finalizado, fica com estado EXPIRADO
def test_finalizar_leilao_sem_lances(sistema_limpo, leilao_valido):
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=2))
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert leilao.estado == EstadoLeilao.EXPIRADO, "Leilão sem lances deve expirar"

# Testa se tentar finalizar um leilão antes da data de término lança erro
def test_finalizar_leilao_antes_da_data(sistema_limpo, leilao_valido):
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    with pytest.raises(ValueError, match="antes da data de término"):
        sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now())

def test_finalizar_leilao_com_lances(sistema_limpo, leilao_valido, participante):
    """Testa se leilão com lances vai para estado FINALIZADO"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    
    # Finaliza após data término (EXIGÊNCIA TESTADA)
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=2))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert leilao.estado == EstadoLeilao.FINALIZADO

def test_estado_pos_finalizacao(sistema_limpo, leilao_valido, participante):
    """Testa o fluxo completo: INATIVO -> ABERTO -> FINALIZADO"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=1))
    
    # Verifica o estado final (EXIGÊNCIA INDIRETA)
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert leilao.estado == EstadoLeilao.FINALIZADO
    assert leilao.identificar_vencedor().participante == participante

# --- Testes de Lances ---

# Testa se adicionar lance quando o leilão está fechado (não aberto) lança erro
def test_adicionar_lance_em_leilao_fechado(sistema_limpo, leilao_valido, participante):
    lance = Lance(600.0, participante.id, leilao_valido.id, datetime.now())
    with pytest.raises(ValueError, match="deve estar ABERTO"):
        sistema_limpo.adicionar_lance(leilao_valido.id, lance)

# Testa se adicionar lance menor que o lance mínimo do leilão lança erro
def test_lance_menor_que_minimo(sistema_limpo, leilao_valido, participante):
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    lance = Lance(400.0, participante.id, leilao_valido.id, datetime.now())
    with pytest.raises(ValueError, match=r"Lance deve ser >= R\$500\.00"):
        sistema_limpo.adicionar_lance(leilao_valido.id, lance)

# --- Testes de Vencedor ---

# Testa se tentar identificar o vencedor antes do leilão ser finalizado lança erro
def test_identificar_vencedor_antes_de_finalizar(sistema_limpo, leilao_valido):
    with pytest.raises(ValueError, match="não finalizado"):
        leilao_valido.identificar_vencedor()

# Fixture que cria uma lista de participantes para testes de lance
@pytest.fixture
def participantes(sistema_limpo):
    return [
        sistema_limpo.adicionar_participante(Participante("111.222.333-44", "João", "joao@email.com", datetime(1990, 1, 1))),
        sistema_limpo.adicionar_participante(Participante("555.666.777-88", "Maria", "maria@email.com", datetime(1985, 5, 15)))
    ]

# Testa se as propriedades maior_lance e menor_lance retornam os valores corretos
def test_propriedades_maior_menor_lance(sistema_limpo, leilao_valido, participantes):
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participantes[0].id, leilao_valido.id, datetime.now()))
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(800.0, participantes[1].id, leilao_valido.id, datetime.now()))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert leilao.maior_lance == 800.0
    assert leilao.menor_lance == 600.0

def test_finalizar_leilao_inativo(sistema_limpo, leilao_valido):
    """Testa que não pode finalizar leilão INATIVO"""
    with pytest.raises(ValueError, match="só pode ser finalizado se estiver ABERTO"):
        sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=2))

def test_finalizar_leilao_ja_finalizado(sistema_limpo, leilao_valido, participante):
    """Testa que não pode finalizar leilão já FINALIZADO"""
    # 1. Abre o leilão
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # 2. Adiciona lance e finaliza
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=2))
    
    # 3. Tenta finalizar novamente
    with pytest.raises(ValueError, match="só pode ser finalizado se estiver ABERTO"):
        sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=3))

def test_finalizar_leilao_expirado(sistema_limpo, leilao_valido):
    """Testa que não pode finalizar leilão EXPIRADO"""
    # 1. Abre e finaliza sem lances (expira)
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=2))
    
    # 2. Tenta finalizar novamente
    with pytest.raises(ValueError, match="só pode ser finalizado se estiver ABERTO"):
        sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=3))

def test_lance_igual_ao_ultimo(sistema_limpo, leilao_valido, participante):
    """Testa que não pode adicionar lance igual ao último"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Primeiro lance válido
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    
    # Tenta adicionar lance com mesmo valor
    with pytest.raises(ValueError) as exc_info:
        sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    
    # Verifica mensagem exata
    assert "Lance deve ser maior que o último lance" in str(exc_info.value)

def test_lance_menor_que_ultimo(sistema_limpo, leilao_valido, participantes):
    """Testa que não pode adicionar lance menor que o último"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Primeiro lance válido
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(1000.0, participantes[0].id, leilao_valido.id, datetime.now()))
    
    # Tenta adicionar lance menor
    with pytest.raises(ValueError) as exc_info:
        sistema_limpo.adicionar_lance(leilao_valido.id, Lance(800.0, participantes[1].id, leilao_valido.id, datetime.now()))
    
    # Verifica mensagem exata
    assert "Lance deve ser maior que o último lance" in str(exc_info.value)

def test_lances_validos_em_sequencia(sistema_limpo, leilao_valido, participantes):
    """Testa sequência válida de lances crescentes"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Lances em ordem crescente
    valores = [600.0, 700.0, 800.0]
    for i, valor in enumerate(valores):
        sistema_limpo.adicionar_lance(leilao_valido.id, Lance(valor, participantes[i % 2].id, leilao_valido.id, datetime.now()))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert len(leilao.lances) == 3
    assert leilao.maior_lance == 800.0

def test_lances_consecutivos_mesmo_participante(sistema_limpo, leilao_valido, participante):
    """Testa que um participante não pode dar dois lances seguidos"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Primeiro lance válido
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    
    # Tenta adicionar segundo lance do mesmo participante
    with pytest.raises(ValueError) as exc_info:
        sistema_limpo.adicionar_lance(leilao_valido.id, Lance(700.0, participante.id, leilao_valido.id, datetime.now()))
    
    # Verifica mensagem exata de erro
    assert "Participante não pode dar dois lances consecutivos" in str(exc_info.value)
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert len(leilao.lances) == 1  # Confirma que o segundo lance não foi adicionado

def test_lances_alternados_participantes_diferentes(sistema_limpo, leilao_valido, participantes):
    """Testa que participantes diferentes podem dar lances alternados"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Primeiro participante
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participantes[0].id, leilao_valido.id, datetime.now()))
    
    # Segundo participante
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(700.0, participantes[1].id, leilao_valido.id, datetime.now()))
    
    # Primeiro participante novamente
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(800.0, participantes[0].id, leilao_valido.id, datetime.now()))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert len(leilao.lances) == 3  # Todos os lances foram aceitos

def test_identificar_vencedor_com_multiplos_lances(sistema_limpo, leilao_valido, participantes):
    """Testa identificação do vencedor com múltiplos lances"""
    # 1. Abre o leilão
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # 2. Adiciona lances em ORDEM CRESCENTE de valores
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participantes[0].id, leilao_valido.id, datetime.now()))
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(700.0, participantes[1].id, leilao_valido.id, datetime.now()))
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(800.0, participantes[0].id, leilao_valido.id, datetime.now()))
    
    # 3. Finaliza o leilão (sem enviar e-mail)
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=1))
    
    # 4. Identifica o vencedor
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    vencedor = leilao.identificar_vencedor()
    
    # 5. Verifica o resultado
    assert vencedor.valor == 800.0  # Maior lance
    assert vencedor.participante == participantes[0]  # Participante correto

def test_identificar_vencedor_com_unico_lance(sistema_limpo, leilao_valido, participante):
    """Testa identificação do vencedor quando há apenas um lance"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=1))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    vencedor = leilao.identificar_vencedor()
    assert vencedor.valor == 600.0
    assert vencedor.participante == participante

def test_identificar_vencedor_com_lances_iguais(sistema_limpo, leilao_valido, participantes):
    """Testa comportamento quando há um único lance máximo"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Adiciona lances com valores crescentes
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(900.0, participantes[0].id, leilao_valido.id, datetime.now()))
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(1000.0, participantes[1].id, leilao_valido.id, datetime.now()))
    
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=1))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    vencedor = leilao.identificar_vencedor()
    assert vencedor.valor == 1000.0
    assert vencedor.participante == participantes[1]  # Último participante com lance máximo

def test_listar_lances_ordenados_com_multiplos_lances(sistema_limpo, leilao_valido, participantes):
    """Testa ordenação com múltiplos lances em ordem crescente"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # Adiciona lances em ORDEM CRESCENTE para respeitar as regras
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(500.0, participantes[0].id, leilao_valido.id, datetime.now()))
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(750.0, participantes[1].id, leilao_valido.id, datetime.now()))
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(1000.0, participantes[0].id, leilao_valido.id, datetime.now()))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    lances_ordenados = leilao.listar_lances_ordenados()
    
    # Verifica ordem e valores
    assert len(lances_ordenados) == 3
    assert lances_ordenados[0].valor == 500.0
    assert lances_ordenados[1].valor == 750.0
    assert lances_ordenados[2].valor == 1000.0
    assert lances_ordenados[0].participante == participantes[0]

def test_listar_lances_ordenados_com_unico_lance(sistema_limpo, leilao_valido, participante):
    """Testa ordenação com apenas um lance"""
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    lances_ordenados = leilao.listar_lances_ordenados()
    
    assert len(lances_ordenados) == 1
    assert lances_ordenados[0].valor == 600.0

def test_str_leilao_finalizado_com_vencedor(sistema_limpo, leilao_valido, participante):
    """Testa representação textual de leilão finalizado com vencedor"""
    # 1. Abre o leilão
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    
    # 2. Adiciona lance
    sistema_limpo.adicionar_lance(leilao_valido.id, Lance(600.0, participante.id, leilao_valido.id, datetime.now()))
    
    # 3. Finaliza o leilão
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=1))
    
    # 4. Verifica a representação textual
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    resultado = str(leilao)
    assert "Leilão: Item Teste (FINALIZADO)" in resultado
    assert "Vencedor: João" in resultado  # Nome do participante da fixture

def test_str_leilao_em_outros_estados(sistema_limpo, leilao_valido):
    """Testa representação textual em estados não finalizados"""
    # Estado INATIVO (padrão)
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert str(leilao) == "Leilão: Item Teste (INATIVO)"
    
    # Estado ABERTO
    sistema_limpo.abrir_leilao(leilao_valido.id, datetime.now())
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert str(leilao) == "Leilão: Item Teste (ABERTO)"
    
    # Estado EXPIRADO (sem lances)
    sistema_limpo.finalizar_leilao(leilao_valido.id, datetime.now() + timedelta(days=1))
    leilao = sistema_limpo.encontrar_leilao_por_id(leilao_valido.id)
    assert str(leilao) == "Leilão: Item Teste (EXPIRADO)"