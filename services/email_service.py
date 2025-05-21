class EmailService:
    @staticmethod
    def enviar(destinatario: str, assunto: str, mensagem: str):
        print(f"📧 E-mail enviado para {destinatario}:")
        print(f"Assunto: {assunto}")
        print(f"Mensagem: {mensagem}\n")
        # Em produção, substituir por um serviço real (SMTP, SendGrid, etc.)