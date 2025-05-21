from services.email_service import EmailService
from datetime import datetime
from enum import Enum, auto

class EstadoLeilao(Enum):
    INATIVO = auto()
    ABERTO = auto()
    FINALIZADO = auto()
    EXPIRADO = auto()

class Leilao:
    def __init__(self, nome: str, lance_minimo: float, data_inicio: datetime, data_fim: datetime):
        if data_fim <= data_inicio:
            raise ValueError("Data de término deve ser posterior à data de início")
            
        self.nome = nome
        self.lance_minimo = lance_minimo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estado = EstadoLeilao.INATIVO
        self.lances = []

    def abrir(self, agora: datetime):
        if self.estado != EstadoLeilao.INATIVO:
            raise ValueError("Leilão só pode ser aberto se estiver INATIVO.")
        if agora < self.data_inicio:
            raise ValueError("Leilão não pode ser aberto antes da data de início.")
        self.estado = EstadoLeilao.ABERTO

    def finalizar(self, agora: datetime, enviar_email: bool = True):
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão só pode ser finalizado se estiver ABERTO.")
        if agora < self.data_fim:
            raise ValueError("Leilão não pode ser finalizado antes da data de término.")
        
        if not self.lances:
            self.estado = EstadoLeilao.EXPIRADO
        else:
            self.estado = EstadoLeilao.FINALIZADO
            if enviar_email:
                vencedor = self.identificar_vencedor().participante
                EmailService.enviar(
                    vencedor.email,
                    "Parabéns! Você venceu o leilão",
                    f"Você arrematou {self.nome} com o lance de R${self.maior_lance:.2f}"
                )

    def adicionar_lance(self, lance):
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão deve estar ABERTO para receber lances.")
        if lance.valor < self.lance_minimo:
            raise ValueError(f"Lance deve ser ≥ R${self.lance_minimo:.2f}")
        if self.lances and lance.valor <= self.lances[-1].valor:
            raise ValueError(f"Lance deve ser > R${self.lances[-1].valor:.2f}")
        if self.lances and lance.participante == self.lances[-1].participante:
            raise ValueError("Participante não pode dar lances consecutivos")
        self.lances.append(lance)

    def identificar_vencedor(self):
        if self.estado != EstadoLeilao.FINALIZADO:
            raise ValueError("Leilão não finalizado")
        return max(self.lances, key=lambda lance: lance.valor)

    def listar_lances_ordenados(self) -> list:
        return sorted(self.lances, key=lambda lance: lance.valor)

    @property
    def maior_lance(self) -> float:
        return max(lance.valor for lance in self.lances) if self.lances else 0

    @property 
    def menor_lance(self) -> float:
        return min(lance.valor for lance in self.lances) if self.lances else 0

    def __str__(self):
        status = f"Leilão: {self.nome} ({self.estado.name})"
        if self.estado == EstadoLeilao.FINALIZADO:
            return f"{status}\nVencedor: {self.identificar_vencedor().participante.nome}"
        return status