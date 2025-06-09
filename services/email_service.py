import smtplib # Biblioteca para enviar e-mails via protocolo SMTP
from email.mime.text import MIMEText # Classe para criar corpo do e-mail em texto simples
from email.mime.multipart import MIMEMultipart # Suporte a múltiplas partes (texto + anexos, por exemplo)
import os  # Acesso a variáveis de ambiente do sistema
from dotenv import load_dotenv # Biblioteca para carregar variáveis de um arquivo .env

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

"""
    Inicializa o serviço de e-mail com as configurações do servidor SMTP.
    As credenciais devem estar armazenadas no arquivo .env como:
    - EMAIL_USER
    - EMAIL_PASSWORD
"""

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com" # Servidor SMTP do Gmail
        self.smtp_port = 587 # Porta usada para TLS (STARTTLS)
        self.email = os.getenv("EMAIL_USER") # Usuário do e-mail
        self.password = os.getenv("EMAIL_PASSWORD") # Senha (ou App Password, se 2FA ativado)

    def enviar(self, destinatario: str, assunto: str, mensagem: str):
        # Cria a estrutura do e-mail (cabeçalhos + corpo)
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = destinatario
        msg['Subject'] = assunto

        # Adiciona o corpo da mensagem como texto simples
        msg.attach(MIMEText(mensagem, 'plain'))

        try:
            # Abre conexão SMTP com servidor Gmail
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()  # Converte conexão para segura (TLS)
                server.login(self.email, self.password) # Autentica no servidor SMTP
                server.send_message(msg) # Envia a mensagem
                print(f"✅ E-mail enviado para {destinatario}")
        except Exception as e:
            # Exibe qualquer erro ocorrido durante o envio
            print(f"❌ Erro ao enviar e-mail: {e}")