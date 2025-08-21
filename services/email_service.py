import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import sys
from jinja2 import Environment, FileSystemLoader

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


class EmailService:
    """
    Serviço de email inteligente com múltiplos modos de operação:
    
    Modos disponíveis:
    - PRODUCTION: Envia emails reais via SMTP
    - DEVELOPMENT: Apenas loga emails no console (não envia)
    - TEST: Simula envio para testes automatizados
    - AUTO: Detecta automaticamente o melhor modo
    """
    
    def __init__(self, modo: Optional[str] = None):
        """
        Inicializa o serviço de email
        
        Args:
            modo: 'production', 'development', 'test', 'auto' ou None
        """
        # Carregar configurações do .env
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.system_name = os.getenv("SYSTEM_NAME", "Sistema de Leilões")
        self.debug = os.getenv("DEBUG_EMAIL", "false").lower() == "true"
        
        # Configurar Jinja2
        self.jinja_env = Environment(loader=FileSystemLoader('templates/'))
        
        # Determinar modo de operação
        if modo is None:
            modo = os.getenv("EMAIL_MODE", "auto")
        
        if modo.lower() == "auto":
            modo = self._detectar_modo()
        
        self.modo = modo.lower()
        
        # Contador de emails para estatísticas
        self.emails_enviados = 0
        self.emails_falharam = 0
        
        # Validar configuração se necessário
        if self.modo == 'production':
            self._validar_configuracao()
        
        # Log de inicialização
        if self.debug:
            logger.info(f"📧 EmailService inicializado:")
            logger.info(f"   Modo: {self.modo}")
            logger.info(f"   Servidor: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"   Email configurado: {'Sim' if self.email else 'Não'}")
    
    def _detectar_modo(self) -> str:
        """Detecta automaticamente o modo baseado no ambiente"""
        # Detectar se está rodando em pytest
        if 'pytest' in sys.modules or 'PYTEST_CURRENT_TEST' in os.environ:
            return 'test'
        
        # Detectar se está em ambiente de CI/CD
        if any(ci_var in os.environ for ci_var in ['CI', 'GITHUB_ACTIONS', 'TRAVIS', 'JENKINS']):
            return 'test'
        
        # Se tem credenciais completas, usar produção
        if self.email and self.password and '@' in self.email:
            return 'production'
        
        # Caso contrário, modo development
        return 'development'
    
    def _validar_configuracao(self):
        """Valida configuração para modo produção"""
        erros = []
        
        if not self.email:
            erros.append("EMAIL_USER não configurado")
        elif '@' not in self.email:
            erros.append("EMAIL_USER deve ser um email válido")
        
        if not self.password:
            erros.append("EMAIL_PASSWORD não configurado")
        
        if erros:
            raise ValueError(
                f"Configuração de email inválida para modo produção:\n" +
                "\n".join(f"- {erro}" for erro in erros) + 
                "\n\nConfigurações necessárias no arquivo .env:\n" +
                "EMAIL_USER=seu.email@gmail.com\n" +
                "EMAIL_PASSWORD=sua_senha_de_app"
            )
    
    def enviar(self, destinatario: str, assunto: str, template: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia email (comportamento varia por modo)
        
        Args:
            destinatario: Email do destinatário
            assunto: Assunto do email
            template: Nome do arquivo de template HTML
            dados: Dicionário com dados para o template
            
        Returns:
            Dict com informações do resultado
        """
        resultado = {
            'sucesso': False,
            'modo': self.modo,
            'destinatario': destinatario,
            'timestamp': datetime.now(),
            'assunto': assunto
        }
        
        try:
            mensagem_html = self.jinja_env.get_template(template).render(dados)
            
            if self.modo == 'test':
                resultado.update(self._enviar_teste(destinatario, assunto, mensagem_html))
            elif self.modo == 'development':
                resultado.update(self._enviar_desenvolvimento(destinatario, assunto, mensagem_html))
            else:  # production
                resultado.update(self._enviar_producao(destinatario, assunto, mensagem_html))
            
            if resultado['sucesso']:
                self.emails_enviados += 1
            else:
                self.emails_falharam += 1
                
        except Exception as e:
            self.emails_falharam += 1
            resultado.update({
                'sucesso': False,
                'erro': str(e)
            })
            logger.error(f"❌ Erro inesperado no envio de email: {e}")
        
        return resultado
    
    def _enviar_teste(self, destinatario: str, assunto: str, mensagem_html: str) -> Dict[str, Any]:
        """Simula envio para testes automatizados"""
        simular_falhas = os.getenv("TEST_SIMULATE_EMAIL_FAILURES", "false").lower() == "true"
        
        if (
            simular_falhas or 
            "falha" in assunto.lower() or 
            "erro" in assunto.lower() or
            "fail" in destinatario.lower()
        ):
            
            if self.debug:
                logger.warning(f"🧪 [TESTE] Simulando falha para: {destinatario}")
            
            return {
                'sucesso': False,
                'erro': 'Falha simulada para teste'
            }
        
        if self.debug:
            logger.info(f"🧪 [TESTE] Email simulado enviado:")
            logger.info(f"    Para: {destinatario}")
            logger.info(f"    Assunto: {assunto}")
            logger.info(f"    Tamanho da mensagem: {len(mensagem_html)} caracteres")
        
        return {'sucesso': True}
    
    def _enviar_desenvolvimento(self, destinatario: str, assunto: str, mensagem_html: str) -> Dict[str, Any]:
        """Log completo para desenvolvimento (não envia email real)"""
        separador = "=" * 60
        
        print(f"\n{separador}")
        print(f"📧 EMAIL QUE SERIA ENVIADO ({self.system_name})")
        print(f"{separador}")
        print(f"De:       {self.email or 'email_nao_configurado@exemplo.com'}")
        print(f"Para:     {destinatario}")
        print(f"Assunto:  {assunto}")
        print(f"Servidor: {self.smtp_server}:{self.smtp_port}")
        print(f"Horário:  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{separador}")
        print("CONTEÚDO HTML:")
        print(mensagem_html)
        print(f"{separador}")
        print("✅ EMAIL LOGADO (NÃO ENVIADO - MODO DESENVOLVIMENTO)")
        print(f"{separador}\n")
        
        return {'sucesso': True}
    
    def _enviar_producao(self, destinatario: str, assunto: str, mensagem_html: str) -> Dict[str, Any]:
        """Envio real para produção"""
        try:
            msg = MIMEMultipart('related')
            msg['From'] = f"{self.system_name} <{self.email}>"
            msg['To'] = destinatario
            msg['Subject'] = assunto
            
            msg.attach(MIMEText(mensagem_html, 'html', 'utf-8'))
            
            # Anexar logo
            try:
                with open('templates/logo.png', 'rb') as f:
                    logo = MIMEImage(f.read())
                    logo.add_header('Content-ID', '<logo>')
                    msg.attach(logo)
            except FileNotFoundError: # pragma: no cover
                logger.warning("Arquivo 'logo.png' não encontrado na pasta 'templates'. O email será enviado sem logo.") # pragma: no cover

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ [PRODUÇÃO] Email enviado para {destinatario}")
            return {'sucesso': True}
            
        except smtplib.SMTPAuthenticationError as e:
            erro = f"Erro de autenticação SMTP: {e}"
            logger.error(f"❌ [PRODUÇÃO] {erro}")
            return {'sucesso': False, 'erro': erro}
            
        except smtplib.SMTPRecipientsRefused as e:
            erro = f"Destinatário rejeitado: {e}"
            logger.error(f"❌ [PRODUÇÃO] {erro}")
            return {'sucesso': False, 'erro': erro}
            
        except smtplib.SMTPException as e:  # pragma: no cover
            erro = f"Erro SMTP: {e}"
            logger.error(f"❌ [PRODUÇÃO] {erro}")
            return {'sucesso': False, 'erro': erro}
            
        except Exception as e:  # pragma: no cover
            erro = f"Erro inesperado: {e}"
            logger.error(f"❌ [PRODUÇÃO] {erro}")
            return {'sucesso': False, 'erro': erro}
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso do serviço"""
        total = self.emails_enviados + self.emails_falharam
        taxa_sucesso = (self.emails_enviados / total * 100) if total > 0 else 0
        
        return {
            'modo': self.modo,
            'emails_enviados': self.emails_enviados,
            'emails_falharam': self.emails_falharam,
            'total_tentativas': total,
            'taxa_sucesso': round(taxa_sucesso, 2),
            'configuracao_valida': bool(self.email and self.password) if self.modo == 'production' else True
        }
    
    def testar_configuracao(self) -> Dict[str, Any]:
        """Testa a configuração atual sem enviar email"""
        resultado = {
            'modo': self.modo,
            'configuracao_ok': False,
            'detalhes': []
        }
        
        if self.modo == 'production':
            if not self.email:
                resultado['detalhes'].append("❌ EMAIL_USER não configurado")
            elif '@' not in self.email:
                resultado['detalhes'].append("❌ EMAIL_USER inválido")
            else:
                resultado['detalhes'].append(f"✅ EMAIL_USER: {self.email}")
            
            if not self.password:
                resultado['detalhes'].append("❌ EMAIL_PASSWORD não configurado")
            else:
                resultado['detalhes'].append("✅ EMAIL_PASSWORD configurado")
            
            resultado['detalhes'].append(f"✅ Servidor: {self.smtp_server}:{self.smtp_port}")
            
            resultado['configuracao_ok'] = bool(self.email and self.password and '@' in self.email)
        else:
            resultado['detalhes'].append(f"✅ Modo {self.modo} - configuração não necessária")
            resultado['configuracao_ok'] = True
        
        return resultado
    
    def __str__(self) -> str:
        """Representação string do serviço"""
        stats = self.obter_estatisticas()
        return (
                f"EmailService(modo={self.modo}, "
                f"enviados={stats['emails_enviados']}, "
                f"falharam={stats['emails_falharam']})"
        )


# Função auxiliar para uso rápido
def enviar_email_rapido(destinatario: str, assunto: str, template: str, dados: Dict[str, Any], modo: str = None) -> bool:
    """
    Função auxiliar para envio rápido de email
    
    Returns:
        bool: True se enviado com sucesso
    """
    service = EmailService(modo)
    resultado = service.enviar(destinatario, assunto, template, dados)
    return resultado['sucesso']


if __name__ == "__main__":  # pragma: no cover
    # Teste rápido do serviço
    print("🧪 Testando EmailService...")
    
    service = EmailService()
    print(f"Modo detectado: {service.modo}")
    
    # Testar configuração
    config_test = service.testar_configuracao()
    print("\nTeste de configuração:")
    for detalhe in config_test['detalhes']:
        print(f"  {detalhe}")
    
    # Teste de envio
    dados_teste = {
        'nome_vencedor': 'Victor',
        'nome_item': 'iPhone 15 Pro',
        'valor_lance': '6000.00',
        'ano': datetime.now().year
    }
    resultado = service.enviar(
        "teste@exemplo.com",
        "Teste do Sistema de Leilões",
        "email_template.html",
        dados_teste
    )
    
    print(f"\nResultado do teste de envio:")
    print(f"  Sucesso: {resultado['sucesso']}")
    print(f"  Modo: {resultado['modo']}")
    
    # Estatísticas
    stats = service.obter_estatisticas()
    print(f"\nEstatísticas: {stats}")
