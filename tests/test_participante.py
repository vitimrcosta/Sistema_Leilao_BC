import pytest
from datetime import datetime
from models.participante import Participante

def test_criacao_participante_valido():
    """Testa a criação com dados válidos"""
    participante = Participante("123.456.789-00", "João", "joao@email.com", datetime(1990, 1, 1))
    assert participante.cpf == "123.456.789-00"

def test_validacao_cpf_invalido():
    """Testa CPF em formato errado"""
    with pytest.raises(ValueError, match="CPF deve estar no formato"):
        Participante("12345678900", "João", "joao@email.com", datetime(1990, 1, 1))

def test_validacao_email_invalido():
    """Testa e-mail mal formatado"""
    with pytest.raises(ValueError, match="E-mail inválido"):
        Participante("123.456.789-00", "João", "emailinvalido", datetime(1990, 1, 1))