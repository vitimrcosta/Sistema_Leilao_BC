from datetime import datetime
from typing import List
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante

# Classe responsável por gerenciar todas as operações relacionadas a leilões e participantes.
class GerenciadorLeiloes:
    def __init__(self):
        # Lista que armazenará todos os objetos do tipo Leilao cadastrados no sistema.
        self.leiloes: List[Leilao] = []
        # Lista que armazenará todos os objetos do tipo Participante cadastrados no sistema.
        self.participantes: List[Participante] = []

    # Remove um participante da lista de participantes do sistema.
    def remover_participante(self, participante):
        #Verifica em todos os leilões se o participante tem lances (any percorre os lances de cada leilão).
        for leilao in self.leiloes:
            # Se o participante tiver feito ao menos um lance em qualquer leilão, lançar exceção.
            if any(lance.participante == participante for lance in leilao.lances):
                raise ValueError("Participante não pode ser removido (possui lances)")
         # Se passou pelas verificações, remove o participante da lista.
        self.participantes.remove(participante)

    # Adiciona um novo leilão.
    def adicionar_leilao(self, leilao: Leilao):
        #Adiciona um novo leilão à lista de leilões.
        self.leiloes.append(leilao)

    def listar_leiloes(self, 
                      estado: EstadoLeilao = None, 
                      data_inicio: datetime = None, 
                      data_fim: datetime = None) -> List[Leilao]:
        """Filtra leilões com base nos critérios fornecidos"""
        resultado = self.leiloes.copy()
    
        # Validação de datas invertidas (CORREÇÃO ADICIONADA)
        if data_inicio is not None and data_fim is not None:
            if data_inicio > data_fim:
                raise ValueError("Data de início não pode ser maior que data de término")
    
        # Filtro por estado
        if estado is not None:
            resultado = [leilao for leilao in resultado if leilao.estado == estado]
    
        # Filtro por intervalo de datas
        if data_inicio is not None and data_fim is not None:
            resultado = [
                leilao for leilao in resultado 
                if leilao.data_inicio >= data_inicio 
                and leilao.data_fim <= data_fim
            ]
        elif data_inicio is not None:
            resultado = [leilao for leilao in resultado if leilao.data_inicio >= data_inicio]
        elif data_fim is not None:
            resultado = [leilao for leilao in resultado if leilao.data_fim <= data_fim]
    
        return resultado

    # Permite editar um leilão específico, desde que ele esteja INATIVO.
    def editar_leilao(self, leilao_id: int, 
                     novo_nome: str = None, 
                     novo_lance_minimo: float = None):
        """Edita um leilão existente"""
         # Busca o leilão correspondente ao ID passado.
        leilao = self._encontrar_leilao_por_id(leilao_id)
        
        # Só permite editar leilões que estão INATIVOS.
        if leilao.estado != EstadoLeilao.INATIVO:
            raise ValueError("Só é possível editar leilões INATIVOS")

         # Se um novo nome foi passado, atualiza o nome.
        if novo_nome:
            leilao.nome = novo_nome

        # Se um novo valor de lance mínimo foi passado, atualiza o valor.
        if novo_lance_minimo:
            leilao.lance_minimo = novo_lance_minimo

    # Remove um leilão do sistema
    def remover_leilao(self, leilao_id: int):
        """Remove um leilão seguindo as regras"""

        # Busca o leilão pelo ID.
        leilao = self._encontrar_leilao_por_id(leilao_id)

        # Regra: não pode remover leilões que estejam ABERTOS.
        if leilao.estado == EstadoLeilao.ABERTO:
            raise ValueError("Não é possível excluir leilões ABERTOS")
        
        # Regra: não pode remover leilões com lances registrados.
        if len(leilao.lances) > 0:
            raise ValueError("Não é possível excluir leilões com lances registrados")
        
        # Se passou pelas regras, remove da lista.
        self.leiloes.remove(leilao)

    # Método auxiliar privado (iniciado por "_") que localiza um leilão a partir do seu ID.
    # Obs: o ID usado aqui é o ID do objeto em memória (usando `id()`), e não um atributo próprio.
    def _encontrar_leilao_por_id(self, leilao_id: int) -> Leilao:
        """Método auxiliar para encontrar leilão por ID"""
        for leilao in self.leiloes:
            if id(leilao) == leilao_id:
                return leilao
        # Se nenhum leilão com esse ID for encontrado, levanta exceção.    
        raise ValueError("Leilão não encontrado")