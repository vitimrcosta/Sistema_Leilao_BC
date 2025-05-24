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