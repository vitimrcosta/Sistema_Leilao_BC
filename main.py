from datetime import datetime, timedelta
from models.leilao import Leilao, EstadoLeilao
from models.participante import Participante
from models.lance import Lance
from models.gerenciador_leiloes import GerenciadorLeiloes
import time

def main():
    # Configuração inicial
    gerenciador = GerenciadorLeiloes()
    
    # Cadastro de participantes (use e-mails reais para teste)
    participante1 = Participante(
        cpf="123.456.789-00",
        nome="Amorzinho",
        email="robertamenezesxavier@gmail.com",
        data_nascimento=datetime(1990, 5, 15)
    )
    participante2 = Participante(
        cpf="987.654.321-00",
        nome="Amorzinho",
        email="robertamenezesxavier@gmail.com",
        data_nascimento=datetime(1985, 8, 20)
    )
    gerenciador.participantes.extend([participante1, participante2])
    
    # Criação do leilão (5 segundos até início, 1 minuto de duração)
    leilao = Leilao(
        nome="iPhone 15 Pro",
        lance_minimo=5000.00,
        data_inicio=datetime.now() + timedelta(seconds=5),
        data_fim=datetime.now() + timedelta(seconds=65)  # 5s + 60s
    )
    gerenciador.adicionar_leilao(leilao)
    
    print("\n=== Leilão criado ===")
    print(f"Início: {leilao.data_inicio.strftime('%H:%M:%S')}")
    print(f"Término: {leilao.data_fim.strftime('%H:%M:%S')}")

    # Aguarda abertura
    print("\nAguardando abertura...")
    while datetime.now() < leilao.data_inicio:
        time.sleep(0.1)
    leilao.abrir(datetime.now())
    print(f"\n=== Leilão ABERTO! ({datetime.now().strftime('%H:%M:%S')}) ===")

    # Registra lances
    print("\n=== Lances ===")
    for valor, participante in [(5500, participante1), (6000, participante2)]:
        try:
            lance = Lance(valor, participante, leilao, datetime.now())
            leilao.adicionar_lance(lance)
            print(f"✅ {lance}")
        except ValueError as e:
            print(f"❌ Erro: {e}")

    # Aguarda término com verificação contínua
    print("\nAguardando término...")
    while True:
        agora = datetime.now()
        if agora >= leilao.data_fim:
            try:
                leilao.finalizar(agora)
                break
            except ValueError as e:
                print(f"Tentando finalizar... ({e})")
                time.sleep(0.5)
        time.sleep(0.5)
    
    # Resultado
    print("\n=== RESULTADO ===")
    print(f"Status: {leilao.estado.name}")
    if leilao.estado == EstadoLeilao.FINALIZADO:
        print(f"Vencedor: {leilao.identificar_vencedor().participante.nome}")
        print(f"Lance vencedor: R${leilao.maior_lance:.2f}")

if __name__ == "__main__":
    main()