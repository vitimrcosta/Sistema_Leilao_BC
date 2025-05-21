from datetime import datetime

class Participante:
    def __init__(self, cpf: str, nome: str, email: str, data_nascimento: datetime):
        self.cpf = cpf
        self.nome = nome
        self.email = email
        self.data_nascimento = data_nascimento

    def __str__(self):
        return f"Participante: {self.nome} (CPF: {self.cpf})"