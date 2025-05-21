import pytest
from datetime import datetime
from models.participante import Participante

def test_criacao_participante():
    data_nasc = datetime(1990, 5, 15)
    p = Participante("123.456.789-00", "João Silva", "joao@email.com", data_nasc)
    assert p.cpf == "123.456.789-00"
    assert p.nome == "João Silva"