import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")

    # Adicione isso para depuração
        print(f"Email: {self.email}, Senha: {'*' * len(self.password) if self.password else 'None'}")

    def enviar(self, destinatario: str, assunto: str, mensagem: str):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = destinatario
        msg['Subject'] = assunto

        msg.attach(MIMEText(mensagem, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()  # Ativa criptografia TLS
                server.login(self.email, self.password)
                server.send_message(msg)
                print(f"✅ E-mail enviado para {destinatario}")
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail: {e}")