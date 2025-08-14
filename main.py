import os
from datetime import datetime, timedelta
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante
from models.lance import Lance
from models.gerenciador_leiloes import GerenciadorLeiloes
from models.database import create_db_tables, get_db
import time
from dotenv import load_dotenv

load_dotenv()

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
        nome="Victor",
        email="victor.rcosta@outlook.com",
        data_nascimento=datetime(2001, 9, 5)
    )
    participante2_data = Participante(
        cpf="987.654.321-00",
        nome="Samuel",
        email="samu.rcosta@gmail.com",
        data_nascimento=datetime(1998, 1, 22)
    )
    participante1 = gerenciador.adicionar_participante(participante1_data)
    participante2 = gerenciador.adicionar_participante(participante2_data)
    
    # Criação do leilão (5 segundos até início, 1 minuto de duração)
    leilao_data = Leilao(
        nome="Notebook Acer Nitro",
        lance_minimo=4500.00,
        data_inicio=datetime.now() + timedelta(seconds=5),
        data_fim=datetime.now() + timedelta(seconds=20)  # 5s + 15s
    )
    leilao = gerenciador.adicionar_leilao(leilao_data)
    
    print("\n=== Leilão criado ===")
    print(f"Início: {leilao.data_inicio.strftime('%H:%M:%S')}")
    print(f"Término: {leilao.data_fim.strftime('%H:%M:%S')}")

    # Aguarda abertura
    print("\nAguardando abertura...")
    while datetime.now() < leilao.data_inicio:
        time.sleep(0.1)
    gerenciador.abrir_leilao(leilao.id, datetime.now())
    print(f"\n=== Leilão ABERTO! ({datetime.now().strftime('%H:%M:%S')}) ===")

    # Registra lances
    print("\n=== Lances ===")
    try:
        gerenciador.adicionar_lance(leilao.id, Lance(5500, participante1.id, leilao.id, datetime.now()))
        print(f"Lance de {participante1.nome} no valor de 5500 adicionado com sucesso!")
        time.sleep(5)
        gerenciador.adicionar_lance(leilao.id, Lance(6000, participante2.id, leilao.id, datetime.now()))
        print(f"Lance de {participante2.nome} no valor de 6000 adicionado com sucesso!")
    except ValueError as e:
        print(f"Erro ao adicionar lance: {e}")

    # Aguarda término com verificação contínua
    print("\nAguardando término...")
    while True:
        agora = datetime.now()
        leilao = gerenciador.encontrar_leilao_por_id(leilao.id)
        if agora >= leilao.data_fim:
            try:
                gerenciador.finalizar_leilao(leilao.id, agora)
                break
            except ValueError as e:
                print(f"Tentando finalizar... ({e})")
                time.sleep(0.5)
        time.sleep(0.5)
    
    # Resultado
    print("\n=== RESULTADO ===")
    leilao = gerenciador.encontrar_leilao_por_id(leilao.id)
    print(f"Status: {leilao.estado.name}")
    if leilao.estado == EstadoLeilao.FINALIZADO:
        vencedor = leilao.identificar_vencedor()
        print(f"Vencedor: {vencedor.participante.nome}")
        print(f"Lance vencedor: R${vencedor.valor:.2f}")
        if os.getenv("EMAIL_MODE") == "production":
            print("\nEmail enviado para o vencedor!")

if __name__ == "__main__":
    main()