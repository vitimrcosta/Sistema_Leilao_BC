from datetime import datetime
from enum import Enum, auto

class EstadoLeilao(Enum):
    INATIVO = auto()
    ABERTO = auto()
    FINALIZADO = auto()
    EXPIRADO = auto()

class Leilao:
    def __init__(self, nome: str, lance_minimo: float, data_inicio: datetime, data_fim: datetime):
        self.nome = nome
        self.lance_minimo = lance_minimo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estado = EstadoLeilao.INATIVO
        self.lances = []  # Armazenará os lances

    def abrir(self, agora: datetime):
        if self.estado != EstadoLeilao.INATIVO:
            raise ValueError("Leilão só pode ser aberto se estiver INATIVO.")
        if agora < self.data_inicio:
            raise ValueError("Leilão não pode ser aberto antes da data de início.")
        self.estado = EstadoLeilao.ABERTO

    def finalizar(self, agora: datetime):
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão só pode ser finalizado se estiver ABERTO.")
        if agora < self.data_fim:
            raise ValueError("Leilão não pode ser finalizado antes da data de término.")
        
        if not self.lances:
            self.estado = EstadoLeilao.EXPIRADO
        else:
            self.estado = EstadoLeilao.FINALIZADO

    def adicionar_lance(self, lance):
        """Adiciona um lance válido ao leilão"""
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão deve estar ABERTO para receber lances.")
        if lance.valor < self.lance_minimo:
            raise ValueError(f"Lance deve ser ≥ R${self.lance_minimo:.2f}")
        if self.lances and lance.valor <= self.lances[-1].valor:
            raise ValueError(f"Lance deve ser > R${self.lances[-1].valor:.2f}")
        if self.lances and lance.participante == self.lances[-1].participante:
            raise ValueError("Participante não pode dar lances consecutivos")
        
        self.lances.append(lance)

    def __str__(self):
        return f"Leilão: {self.nome} ({self.estado.name})"