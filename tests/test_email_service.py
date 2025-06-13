import pytest
from unittest.mock import patch, MagicMock
from services.email_service import EmailService
import smtplib

@pytest.fixture
def email_service():
    """Fixture que fornece uma instância do EmailService para os testes"""
    return EmailService()

def test_enviar_email_sucesso(email_service):
    """Testa o envio de email bem-sucedido"""
    with patch('smtplib.SMTP') as mock_smtp:
        # Configura o mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Chama o método a ser testado
        email_service.enviar(
            destinatario="victor@outlook.com",
            assunto="Assunto Teste",
            mensagem="Testando o email"
        )
        
        # Verificações
        mock_smtp.assert_called_once_with(
            email_service.smtp_server,
            email_service.smtp_port,
            timeout=30
        )
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            email_service.email,
            email_service.password
        )
        assert mock_server.send_message.called

def test_enviar_email_falha_conexao(email_service):
    """Testa falha na conexão SMTP"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPException("Erro de conexão")
        
        # Testa que não levanta exceção (apenas imprime o erro)
        email_service.enviar(
            destinatario="victor@outlook.com",
            assunto="Falha conexão SMTP",
            mensagem="Testa falha na conexão SMTP"
        )
        
        mock_smtp.assert_called_once()

def test_enviar_email_falha_autenticacao(email_service):
    """Testa falha na autenticação"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, b'Authentication failed'
        )
        
        email_service.enviar(
            destinatario="victor@outlook.com",
            assunto="Falha na autenticação",
            mensagem="Testa falha na autenticação"
        )
        
        mock_server.login.assert_called_once()

def test_enviar_email_falha_envio(email_service):
    """Testa falha no envio da mensagem"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.send_message.side_effect = smtplib.SMTPException("Erro no envio")
        
        email_service.enviar(
            destinatario="victor@outlook.com",
            assunto="Falha no envio da mensagem",
            mensagem="Testa falha no envio da mensagem"
        )
        
        mock_server.send_message.assert_called_once()