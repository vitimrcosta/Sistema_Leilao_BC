from datetime import datetime
import re # Módulo de expressões regulares, usado para validações de formato

# Classe que representa um participante do sistema de leilão.
class Participante:
    def __init__(self, cpf: str, nome: str, email: str, data_nascimento: datetime):
        self.cpf = self._validar_cpf(cpf)
        self.nome = nome
        self.email = self._validar_email(email)
        self.data_nascimento = data_nascimento

    # Método privado (_ indica que não deve ser chamado diretamente fora da classe)
    def _validar_cpf(self, cpf: str) -> str:
        """ A regex verifica exatamente o formato 069.412.581-44"""
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            raise ValueError("CPF deve estar no formato 123.456.789-00")
        return cpf

    # Método privado para validar o e-mail.
    def _validar_email(self, email: str) -> str:
        # A regex garante que exista algo antes do @, algo depois do @, seguido de ponto e uma extensão.
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("E-mail inválido")
        return email