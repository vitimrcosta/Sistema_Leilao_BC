# Tests/conftest.py - Configurações globais para os testes de integração
import pytest
import sys
import os
from datetime import datetime, timedelta
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.participante import Participante
from models.leilao import Leilao


@pytest.fixture(scope="session")
def email_test_config():
    """Configuração global para testes de email"""
    return {
        'smtp_server': 'localhost',
        'smtp_port': 1025,  # Porta para servidor SMTP de teste
        'timeout': 5
    }


@pytest.fixture
def sistema_limpo():
    """Fixture que garante um sistema limpo para cada teste"""
    return GerenciadorLeiloes()


@pytest.fixture
def participantes_padrao():
    """Fixture com participantes padrão para testes"""
    return [
        Participante("111.111.111-11", "Alice Silva", "alice@test.com", datetime(1990, 1, 1)),
        Participante("222.222.222-22", "Bob Santos", "bob@test.com", datetime(1985, 6, 15)),
        Participante("333.333.333-33", "Carol Lima", "carol@test.com", datetime(1988, 12, 10)),
    ]


@pytest.fixture
def leilao_padrao():
    """Fixture com leilão configurado para testes"""
    agora = datetime.now()
    return Leilao(
        "Produto Teste", 1000.0,
        agora - timedelta(minutes=5),  # Pode ser aberto
        agora + timedelta(minutes=5)   # Fecha em 5 minutos
    )


# Marcadores personalizados para categorizar os testes
def pytest_configure(config):
    """Configuração personalizada do pytest"""
    config.addinivalue_line(
        "markers", "integracao: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "email: marca testes que envolvem email"
    )
    config.addinivalue_line(
        "markers", "tempo_real: marca testes que dependem de tempo real"
    )
    config.addinivalue_line(
        "markers", "complexo: marca testes com cenários complexos"
    )


@pytest.fixture(autouse=True)
def limpar_ambiente():
    """Fixture que executa antes e depois de cada teste para garantir ambiente limpo"""
    # Setup: executado antes de cada teste
    yield  # Aqui o teste é executado
    # Teardown: executado depois de cada teste
    # Você pode adicionar limpeza aqui se necessário
    pass