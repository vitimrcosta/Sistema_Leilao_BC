from datetime import datetime
import re

class Participante:
    def __init__(self, cpf: str, nome: str, email: str, data_nascimento: datetime):
        self.cpf = self._validar_cpf(cpf)
        self.nome = nome
        self.email = self._validar_email(email)
        self.data_nascimento = data_nascimento

    #Verifica se o CPF está no formato 123.456.789-00 (com pontos e hífen).
    def _validar_cpf(self, cpf: str) -> str:
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            raise ValueError("CPF deve estar no formato 123.456.789-00")
        return cpf

    #Verifica se o e-mail tem um formato válido (usuario@dominio.extensao).
    def _validar_email(self, email: str) -> str:
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("E-mail inválido")
        return email