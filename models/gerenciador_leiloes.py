from datetime import datetime
from typing import List
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

class GerenciadorLeiloes:
    def __init__(self):
        self.leiloes: List[Leilao] = []
        self.participantes: list[Participante] = []

    def remover_participante(self, participante):
        for leilao in self.leiloes:
            if any(lance.participante == participante for lance in leilao.lances):
                raise ValueError("Participante não pode ser removido (possui lances)")
        self.participantes.remove(participante)        

    def adicionar_leilao(self, leilao: Leilao):
        self.leiloes.append(leilao)

    def listar_leiloes(self, estado: EstadoLeilao = None, data_inicio: datetime = None, data_fim: datetime = None) -> List[Leilao]:
        resultado = self.leiloes.copy()
        
        # Filtro por estado
        if estado:
            resultado = [leilao for leilao in resultado if leilao.estado == estado]
        
        # Filtro por intervalo de datas
        if data_inicio:
            resultado = [leilao for leilao in resultado if leilao.data_inicio >= data_inicio]
        if data_fim:
            resultado = [leilao for leilao in resultado if leilao.data_fim <= data_fim]
        
        return resultado