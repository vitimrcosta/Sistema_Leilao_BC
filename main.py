import os
from datetime import datetime, timedelta
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante
from models.lance import Lance
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.database import create_db_tables, get_db
import time

def main():
    if os.path.exists("leilao.db"):
        os.remove("leilao.db")
        
    create_db_tables()
    db = next(get_db())
    
    # Configuração inicial
    gerenciador = GerenciadorLeiloes(db)
    
    # Cadastro de participantes (use e-mails reais para teste)
    participante1_data = Participante(
        cpf="123.456.789-00",
        nome="Roberta",
        email="robertamenezesxavier1@gmail.com",
        data_nascimento=datetime(1990, 5, 15)
    )
    participante2_data = Participante(
        cpf="987.654.321-00",
        nome="Victor",
        email="robertamenezesxavier2@gmail.com",
        data_nascimento=datetime(1985, 8, 20)
    )
    participante1 = gerenciador.adicionar_participante(participante1_data)
    participante2 = gerenciador.adicionar_participante(participante2_data)
    
    # Criação do leilão (5 segundos até início, 1 minuto de duração)
    leilao_data = Leilao(
        nome="iPhone 15 Pro",
        lance_minimo=5000.00,
        data_inicio=datetime.now() + timedelta(seconds=5),
        data_fim=datetime.now() + timedelta(seconds=65)  # 5s + 60s
    )
    leilao = gerenciador.adicionar_leilao(leilao_data)
    
    print("\n=== Leilão criado ===")
    print(f"Início: {leilao.data_inicio.strftime('%H:%M:%S')}")
    print(f"Término: {leilao.data_fim.strftime('%H:%M:%S')}")

    # Aguarda abertura
    print("\nAguardando abertura...")
    while datetime.now() < leilao.data_inicio:
        time.sleep(0.1)
    leilao.abrir(datetime.now())
    db.commit()
    print(f"\n=== Leilão ABERTO! ({datetime.now().strftime('%H:%M:%S')}) ===")

    # Registra lances
    print("\n=== Lances ===")
    for valor, participante_obj in [(5500, participante1), (6000, participante2)]:
        try:
            lance = Lance(valor, participante_obj.id, leilao.id, datetime.now())
            
            # Explicitly load the lances relationship
            leilao.lances = db.query(Lance).filter(Lance.leilao == leilao).order_by(Lance.data_hora).all()

            # Validar valor do lance
            if not leilao.lances:
                if lance.valor < leilao.lance_minimo:
                    raise ValueError(f"O primeiro lance deve ser de pelo menos R${leilao.lance_minimo:.2f}")
            else:
                if lance.valor <= leilao.lances[-1].valor:
                    raise ValueError(f"O lance deve ser maior que o último lance de R${leilao.lances[-1].valor:.2f}")

            # Mesmo participante não pode dar lances consecutivos
            if leilao.lances and lance.participante == leilao.lances[-1].participante:
                raise ValueError("Participante não pode dar lances consecutivos")

            db.add(lance)
            db.commit()
            db.refresh(leilao)
            print(f"Lance adicionado: {lance}")
        except ValueError as e:
            print(f"Erro ao adicionar lance: {e}")

    # Aguarda término com verificação contínua
    print("\nAguardando término...")
    while True:
        agora = datetime.now()
        if agora >= leilao.data_fim:
            try:
                leilao.finalizar(agora)
                db.commit()
                break
            except ValueError as e:
                print(f"Tentando finalizar... ({e})")
                time.sleep(0.5)
        time.sleep(0.5)
    
    # Resultado
    print("\n=== RESULTADO ===")
    print(f"Status: {leilao.estado.name}")
    if leilao.estado == EstadoLeilao.FINALIZADO:
        vencedor = leilao.identificar_vencedor()
        print(f"Vencedor: {vencedor.participante.nome}")
        print(f"Lance vencedor: R${vencedor.valor:.2f}")

if __name__ == "__main__":
    main()