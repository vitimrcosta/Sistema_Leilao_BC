from datetime import datetime

class Lance:
    def __init__(self, valor: float, participante, leilao, data_hora: datetime):
        self.valor = valor
        self.participante = participante  # Objeto que representa quem deu o lance.
        self.leilao = leilao              # Objeto que representa o leilão onde o lance foi dado.
        self.data_hora = data_hora        # Momento exato em que o lance foi feito.

    @property
    def valor(self):
        return self._valor  # Sem setter = atributo read-only

    def __str__(self):
        return f"Lance de R${self.valor:.2f} por {self.participante.nome}"