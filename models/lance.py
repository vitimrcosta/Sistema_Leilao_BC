from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class Lance(Base):
    __tablename__ = "lances"

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    leilao_id = Column(Integer, ForeignKey("leiloes.id"), nullable=False)
    data_hora = Column(DateTime, nullable=False)

    # Relacionamentos
    participante = relationship("Participante", back_populates="lances")
    leilao = relationship("Leilao", back_populates="lances")

    def __init__(self, valor: float, participante_id: int, leilao_id: int, data_hora: datetime):
        self.valor = valor
        self.participante_id = participante_id
        self.leilao_id = leilao_id
        self.data_hora = data_hora

    def __str__(self):
        return f"Lance de R${self.valor:.2f} por {self.participante.nome}"

    def __repr__(self):
        return f"<Lance(id={self.id}, valor={self.valor}, participante_id={self.participante_id}, leilao_id={self.leilao_id})>"