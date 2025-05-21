from services.email_service import EmailService
from io import StringIO
import sys

def test_envio_email(capsys):
    EmailService.enviar("comprador@email.com", "Teste", "Mensagem de teste")
    captured = capsys.readouterr()
    assert "comprador@email.com" in captured.out