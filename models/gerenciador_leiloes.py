from datetime import datetime
from typing import List
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

class GerenciadorLeiloes:
    def __init__(self):
        self.leiloes: List[Leilao] = []
        self.participantes: List[Participante] = []

    def remover_participante(self, participante):
        for leilao in self.leiloes:
            if any(lance.participante == participante for lance in leilao.lances):
                raise ValueError("Participante não pode ser removido (possui lances)")
        self.participantes.remove(participante)

    def adicionar_leilao(self, leilao: Leilao):
        self.leiloes.append(leilao)

    def listar_leiloes(self, 
                      estado: EstadoLeilao = None, 
                      data_inicio: datetime = None, 
                      data_fim: datetime = None) -> List[Leilao]:
        """Filtra leilões com base nos critérios fornecidos"""
        resultado = self.leiloes.copy()
        
        # Filtro por estado
        if estado is not None:
            resultado = [leilao for leilao in resultado if leilao.estado == estado]
        
        # Filtro por intervalo de datas
        if data_inicio is not None:
            resultado = [leilao for leilao in resultado if leilao.data_inicio >= data_inicio]
        if data_fim is not None:
            resultado = [leilao for leilao in resultado if leilao.data_fim <= data_fim]
        
        return resultado

    def editar_leilao(self, leilao_id: int, 
                     novo_nome: str = None, 
                     novo_lance_minimo: float = None):
        """Edita um leilão existente"""
        leilao = self._encontrar_leilao_por_id(leilao_id)
        
        if leilao.estado != EstadoLeilao.INATIVO:
            raise ValueError("Só é possível editar leilões INATIVOS")

        if novo_nome:
            leilao.nome = novo_nome
        if novo_lance_minimo:
            leilao.lance_minimo = novo_lance_minimo

    def remover_leilao(self, leilao_id: int):
        """Remove um leilão seguindo as regras:
        - Não pode remover leilões ABERTOS
        - Não pode remover leilões com lances (mesmo inativos ou finalizados)
        - Pode remover leilões INATIVOS sem lances
        """
        leilao = self._encontrar_leilao_por_id(leilao_id)
    
        if leilao.estado == EstadoLeilao.ABERTO:
            raise ValueError("Não é possível excluir leilões ABERTOS")
        
        if len(leilao.lances) > 0:
            raise ValueError("Não é possível excluir leilões com lances registrados")
        
        self.leiloes.remove(leilao)

    def _encontrar_leilao_por_id(self, leilao_id: int) -> Leilao:
        """Método auxiliar para encontrar leilão por ID"""
        for leilao in self.leiloes:
            if id(leilao) == leilao_id:
                return leilao
        raise ValueError("Leilão não encontrado")