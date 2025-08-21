from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante
from models.lance import Lance
from services.email_service import EmailService

# Classe responsável por gerenciar todas as operações relacionadas a leilões e participantes.
class GerenciadorLeiloes:
    def __init__(self, db: Session):
        self.db = db

    # Adiciona um novo leilão.
    def adicionar_leilao(self, leilao: Leilao):
        self.db.add(leilao)
        self.db.commit()
        self.db.refresh(leilao)
        return leilao

    def adicionar_participante(self, participante: Participante):
        self.db.add(participante)
        self.db.commit()
        self.db.refresh(participante)
        return participante

    def encontrar_leilao_por_id(self, leilao_id: int) -> Leilao:
        return self.db.query(Leilao).filter(Leilao.id == leilao_id).first()

    def encontrar_participante_por_cpf(self, cpf: str) -> Participante:
        return self.db.query(Participante).filter(Participante.cpf == cpf).first()

    def abrir_leilao(self, leilao_id: int, data_abertura: datetime):
        leilao = self.encontrar_leilao_por_id(leilao_id)
        if not leilao:
            raise ValueError("Leilão não encontrado")
        leilao.abrir(data_abertura)
        self.db.commit()

    def finalizar_leilao(self, leilao_id: int, data_finalizacao: datetime):
        leilao = self.encontrar_leilao_por_id(leilao_id)
        if not leilao:
            raise ValueError("Leilão não encontrado")
        
        leilao.finalizar(data_finalizacao)
        self.db.commit()

        # Se o leilão foi finalizado com um vencedor, envia o e-mail.
        if leilao.estado == EstadoLeilao.FINALIZADO:
            try:
                vencedor = leilao.identificar_vencedor().participante
                email_service = EmailService()
                email_service.enviar(
                    vencedor.email,
                    f"Parabéns! Você venceu o leilão '{leilao.nome}'",
                    "email_template.html",
                    {
                        "nome_vencedor": vencedor.nome,
                        "nome_item": leilao.nome,
                        "valor_lance": f"{leilao.maior_lance:.2f}",
                        "ano": datetime.now().year
                    }
                )
            except Exception as e:
                # Mesmo que o e-mail falhe, o leilão já foi finalizado.
                # Apenas registra o erro para análise posterior.
                print(f"ALERTA: Leilão ID {leilao.id} finalizado, mas o e-mail para o vencedor falhou: {e}")

    def adicionar_lance(self, leilao_id: int, lance: Lance):
        leilao = self.encontrar_leilao_por_id(leilao_id)
        if not leilao:
            raise ValueError("Leilão não encontrado")
        
        if leilao.estado != EstadoLeilao.ABERTO:
            raise ValueError("Leilão deve estar ABERTO para receber lances")

        if lance.valor < leilao.lance_minimo:
            raise ValueError(f"Lance deve ser >= R${leilao.lance_minimo:.2f}")

        if leilao.lances and lance.valor <= leilao.lances[-1].valor:
            raise ValueError("Lance deve ser maior que o último lance")

        if leilao.lances and lance.participante_id == leilao.lances[-1].participante_id:
            raise ValueError("Participante não pode dar dois lances consecutivos")

        self.db.add(lance)
        self.db.commit()

    def listar_leiloes(self, 
                      estado: EstadoLeilao = None, 
                      data_inicio: datetime = None, 
                      data_fim: datetime = None) -> List[Leilao]:
        query = self.db.query(Leilao)
        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValueError("Data de início não pode ser maior que data de término")
        if estado:
            query = query.filter(Leilao.estado == estado)
        if data_inicio:
            query = query.filter(Leilao.data_inicio >= data_inicio)
        if data_fim:
            query = query.filter(Leilao.data_fim <= data_fim)
        return query.all()

    def editar_leilao(self, leilao_id: int, 
                     novo_nome: str = None, 
                     novo_lance_minimo: float = None):
        leilao = self.encontrar_leilao_por_id(leilao_id)
        if not leilao:
            raise ValueError("Leilão não encontrado")
        
        if leilao.estado != EstadoLeilao.INATIVO:
            raise ValueError("Só é possível editar leilões INATIVOS")

        if novo_nome:
            leilao.nome = novo_nome
        if novo_lance_minimo:
            leilao.lance_minimo = novo_lance_minimo
        
        self.db.commit()
        self.db.refresh(leilao)
        return leilao

    def remover_leilao(self, leilao_id: int):
        leilao = self.encontrar_leilao_por_id(leilao_id)
        if not leilao:
            raise ValueError("Leilão não encontrado")

        if leilao.estado == EstadoLeilao.ABERTO:
            raise ValueError("Não é possível excluir leilões ABERTOS")
        
        if leilao.lances:
            raise ValueError("Não é possível excluir leilões com lances registrados")
        
        self.db.delete(leilao)
        self.db.commit()

    def remover_participante(self, participante: Participante):
        participante_db = self.encontrar_participante_por_cpf(participante.cpf)
        if not participante_db:
            raise ValueError("Participante não encontrado")

        # Verifica se o participante tem lances
        lances = self.db.query(Lance).filter(Lance.participante_id == participante_db.id).count()
        if lances > 0:
            raise ValueError("Participante não pode ser removido (possui lances)")

        self.db.delete(participante_db)
        self.db.commit()