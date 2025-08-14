from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import re
from models.base import Base

class Participante(Base):
    __tablename__ = "participantes"
    
    # Campos do banco de dados
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    data_nascimento = Column(DateTime, nullable=False)
    
    # Relacionamentos
    lances = relationship("Lance", back_populates="participante")
    
    def __init__(self, cpf: str, nome: str, email: str, data_nascimento: datetime):
        self.cpf = self._validar_cpf(cpf)
        self.nome = nome
        self.email = self._validar_email(email)
        self.data_nascimento = data_nascimento
    
    def _validar_cpf(self, cpf: str) -> str:
        """Validação do CPF no formato 123.456.789-00"""
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            raise ValueError("CPF deve estar no formato 123.456.789-00")
        return cpf
    
    def _validar_email(self, email: str) -> str:
        """Validação básica do e-mail"""
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("E-mail inválido")
        return email
    
    def __str__(self):
        return f"Participante: {self.nome} ({self.cpf})"
    
    def __repr__(self):
        return f"<Participante(id={self.id}, nome='{self.nome}', cpf='{self.cpf}')>"
    
    def __eq__(self, other):
        if isinstance(other, Participante):
            return self.cpf == other.cpf
        return False
    
    def __hash__(self):
        return hash(self.cpf)