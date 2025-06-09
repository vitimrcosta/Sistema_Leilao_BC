from services.email_service import EmailService

def test_envio_real():
    email = EmailService()
    email.enviar(
        "victor.rcosta@outlook.com",
        "Teste de Leilão - Não Responder",
        "Este é um teste automático do sistema de leilões. Pode ignorar."
    )
    print("Verifique sua caixa de entrada e spam!")

if __name__ == "__main__":
    test_envio_real()