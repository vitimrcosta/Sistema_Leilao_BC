from datetime import datetime
from enum import Enum, auto

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from models.base import Base

# Enumeração dos possíveis estados de um leilão
class EstadoLeilao(Enum):
    INATIVO = auto()    # Estado inicial: o leilão ainda não começou (antes da data_inicio)
    ABERTO = auto()     # Leilão está em andamento e pode receber lances
    FINALIZADO = auto() # Leilão foi encerrado com sucesso (pelo menos um lance foi feito)
    EXPIRADO = auto()   # Leilão foi encerrado sem que nenhum lance tenha sido feito

# Classe que representa um Leilão
class Leilao(Base):
    __tablename__ = "leiloes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    lance_minimo = Column(Float, nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    estado = Column(SQLEnum(EstadoLeilao), default=EstadoLeilao.INATIVO, nullable=False)

    # Relacionamento com Lances (um leilão pode ter muitos lances)
    lances = relationship("Lance", back_populates="leilao", cascade="all, delete-orphan")

    def __init__(self, nome: str, lance_minimo: float, data_inicio: datetime, data_fim: datetime):
        # Validação para garantir que a data final não seja anterior à inicial
        if data_fim <= data_inicio:
            raise ValueError("Data de término deve ser posterior à data de início")
        self.nome = nome
        self.lance_minimo = lance_minimo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estado = EstadoLeilao.INATIVO

    # Método para abrir o leilão
    def abrir(self, agora: datetime):
        # Só pode abrir se estiver INATIVO
        if self.estado != EstadoLeilao.INATIVO:
            raise ValueError("Leilão só pode ser aberto se estiver INATIVO.")
        # Não pode abrir antes da data de início
        if agora < self.data_inicio:
            raise ValueError("Leilão não pode ser aberto antes da data de início.")
        # Se tudo certo, muda o estado para ABERTO
        self.estado = EstadoLeilao.ABERTO

    # Método para finalizar o leilão
    def finalizar(self, agora: datetime):
        # Só pode finalizar se estiver ABERTO
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão só pode ser finalizado se estiver ABERTO.")
        # Só pode finalizar se já passou da data de término
        if agora < self.data_fim:
            raise ValueError("Leilão não pode ser finalizado antes da data de término.")
        
        # Se não houver lances, leilão expira
        if not self.lances: # Verifica se não há lances
            self.estado = EstadoLeilao.EXPIRADO
        else:
            # Se tiver lances, leilão é finalizado
            self.estado = EstadoLeilao.FINALIZADO

    # Método para identificar o vencedor (maior lance)
    def identificar_vencedor(self):
        # Só pode identificar se o leilão estiver FINALIZADO
        if self.estado != EstadoLeilao.FINALIZADO:
            raise ValueError("Leilão não finalizado")
        # Retorna o lance com maior valor
        return max(self.lances, key=lambda lance: lance.valor)

    # Método que retorna os lances ordenados por valor (do menor para o maior)
    def listar_lances_ordenados(self) -> list:
        return sorted(self.lances, key=lambda lance: lance.valor)

    # Propriedade para acessar o maior valor de lance (retorna 0 se não houver lances)
    @property
    def maior_lance(self) -> float:
        return max(lance.valor for lance in self.lances) if self.lances else 0

     # Propriedade para acessar o menor valor de lance (retorna 0 se não houver lances)
    @property 
    def menor_lance(self) -> float:
        return min(lance.valor for lance in self.lances) if self.lances else 0

    # Representação textual do leilão (usada ao dar print no objeto)
    def __str__(self):
        status = f"Leilão: {self.nome} ({self.estado.name})"
        # Se o leilão foi finalizado, mostra também o nome do vencedor
        if self.estado == EstadoLeilao.FINALIZADO:
            return f"{status}\nVencedor: {self.identificar_vencedor().participante.nome}"
         # Caso contrário, mostra apenas o nome e estado
        return status

    def __repr__(self):
        return f"<Leilao(id={self.id}, nome='{self.nome}', estado={self.estado.name})>"
