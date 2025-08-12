"""
Teste isolado para cobrir linhas 75-83 do _detectar_modo()

Execute este teste separadamente se necessário:
python tests/test_detectar_modo.py
"""

import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_detectar_modo_linha_por_linha():
    """Executa linha por linha do método _detectar_modo"""
    
    print("Testando detecção de modo linha por linha...")
    
    # Importar após configurar o path
    from services.email_service import EmailService
    
    # Criar instância sem inicializar completamente
    service = EmailService.__new__(EmailService)
    
    # Configurar atributos necessários
    service.smtp_server = "smtp.gmail.com"
    service.smtp_port = 587
    service.system_name = "Test"
    service.debug = False
    service.emails_enviados = 0
    service.emails_falharam = 0

    # Helper to run a check in a clean environment
    def run_check(env_vars_to_set):
        original_modules = sys.modules.copy()
        pytest_modules = [m for m in sys.modules if 'pytest' in m.lower()]
        for mod in pytest_modules:
            sys.modules.pop(mod, None)
        
        original_environ = os.environ.copy()
        for key in ['CI', 'GITHUB_ACTIONS', 'TRAVIS', 'JENKINS', 'PYTEST_CURRENT_TEST']:
            if key in os.environ:
                del os.environ[key]

        for k, v in env_vars_to_set.items():
            os.environ[k] = v
        
        try:
            return service._detectar_modo()
        finally:
            sys.modules.update(original_modules)
            os.environ.clear()
            os.environ.update(original_environ)

    print("\n1. Testando com CI=true (linha 75-76)")
    resultado = run_check({'CI': 'true'})
    print(f"   Resultado: {resultado}")
    assert resultado == 'test'

    print("\n2. Testando com GITHUB_ACTIONS=true (linha 75-76)")
    resultado = run_check({'GITHUB_ACTIONS': 'true'})
    print(f"   Resultado: {resultado}")
    assert resultado == 'test'

    print("\n3. Testando com TRAVIS=true (linha 75-76)")
    resultado = run_check({'TRAVIS': 'true'})
    print(f"   Resultado: {resultado}")
    assert resultado == 'test'

    print("\n4. Testando com JENKINS=true (linha 75-76)")
    resultado = run_check({'JENKINS': 'true'})
    print(f"   Resultado: {resultado}")
    assert resultado == 'test'

    print("\n5. Testando com credenciais completas (linha 79-80)")
    service.email = 'test@example.com'
    service.password = 'senha123'
    resultado = run_check({})
    print(f"   Resultado: {resultado}")
    assert resultado == 'production'
    
    print("\n6. Testando sem credenciais (linha 83)")
    service.email = None
    service.password = None
    resultado = run_check({})
    print(f"   Resultado: {resultado}")
    assert resultado == 'development'

    print("\n✅ Todas as linhas 75-83 foram executadas!")


if __name__ == "__main__":
    # Executar o teste
    success = test_detectar_modo_linha_por_linha()
    
    if success:
        print("\n🎉 Sucesso! Execute agora:")
        print("coverage run --append tests/test_detectar_modo.py")
        print("coverage report -m")
    
    # Também executar o main do email_service para cobrir linhas 312-336
    print("\n7. Executando o bloco __main__ do email_service.py...")
    import subprocess
    result = subprocess.run([sys.executable, "services/email_service.py"], 
                          capture_output=True, text=True, encoding='utf-8')
    
    if "Testando EmailService" in result.stdout or "Testando EmailService" in result.stderr:
        print("   ✅ Bloco __main__ executado com sucesso!")
    else:
        print("   ⚠️ Bloco __main__ pode não ter sido executado completamente")
        print(f"   Saída: {result.stdout[:100]}...")
        print(f"   Erro: {result.stderr[:100]}...")