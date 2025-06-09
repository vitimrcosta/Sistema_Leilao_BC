from services.email_service import EmailService
from datetime import datetime
from enum import Enum, auto

# Enumeração dos possíveis estados de um leilão
class EstadoLeilao(Enum):
    INATIVO = auto() # Estado inicial do leilão, antes da data de início
    ABERTO = auto() # Leilão aberto para receber lances
    FINALIZADO = auto() # Leilão encerrado com pelo menos um lance
    EXPIRADO = auto() # Leilão encerrado sem nenhum lance

# Classe que representa um Leilão
class Leilao:
     # Método construtor: inicializa os dados de um novo leilão
    def __init__(self, nome: str, lance_minimo: float, data_inicio: datetime, data_fim: datetime):
        # Validação: data de término deve ser depois da data de início
        if data_fim <= data_inicio:
            raise ValueError("Data de término deve ser posterior à data de início")
        # Atributos básicos do leilão
        self.nome = nome # Nome do item a ser leiloado
        self.lance_minimo = lance_minimo  # Valor mínimo para aceitar lances
        self.data_inicio = data_inicio  # Data/hora de início do leilão
        self.data_fim = data_fim # Data/hora de término do leilão
        self.estado = EstadoLeilao.INATIVO # Estado inicial do leilão
        self.lances = [] # Lista de lances recebidos

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
    def finalizar(self, agora: datetime, enviar_email: bool = True):
        # Só pode finalizar se estiver ABERTO
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão só pode ser finalizado se estiver ABERTO.")
        # Só pode finalizar se já passou da data de término
        if agora < self.data_fim:
            raise ValueError("Leilão não pode ser finalizado antes da data de término.")
        
        # Se não houver lances, leilão expira
        if not self.lances:
            self.estado = EstadoLeilao.EXPIRADO
        else:
            # Se tiver lances, leilão é finalizado
            self.estado = EstadoLeilao.FINALIZADO
            vencedor = max(self.lances, key=lambda lance: lance.valor).participante
            # Envia e-mail de forma síncrona
            email_service = EmailService()
            email_service.enviar(
                vencedor.email,
                "Parabéns! Você venceu o leilão",
                f"""Olá {vencedor.nome},
            
                Você venceu o leilão do item '{self.nome}' com o lance de R${max(l.valor for l in self.lances):.2f}.

                Atenciosamente,
                Sistema de Leilões
                """
            )
            
    # Método para adicionar um novo lance no leilão
    def adicionar_lance(self, lance):
        # Leilão deve estar ABERTO
        if self.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão deve estar ABERTO para receber lances.")
        # Lance deve respeitar o lance mínimo
        if lance.valor < self.lance_minimo:
            raise ValueError(f"Lance deve ser ≥ R${self.lance_minimo:.2f}")
         # Lance deve ser maior que o último lance
        if self.lances and lance.valor <= self.lances[-1].valor:
            raise ValueError(f"Lance deve ser > R${self.lances[-1].valor:.2f}")
        # Mesmo participante não pode dar lances consecutivos
        if self.lances and lance.participante == self.lances[-1].participante:
            raise ValueError("Participante não pode dar lances consecutivos")
        # Se passou em todas as validações, adiciona o lance à lista
        self.lances.append(lance)

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