#!/usr/bin/env python3
"""
Script para verificar e melhorar a cobertura de testes
"""

import subprocess
import sys
import os


def run_command(command, description=""):
    """Executa comando e mostra resultado"""
    print(f"\n{'='*60}")
    if description:
        print(f"📋 {description}")
    print(f"🔧 Executando: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    print("📤 SAÍDA:")
    print(result.stdout)
    
    if result.stderr:
        print("⚠️  ERROS:")
        print(result.stderr)
    
    print(f"✅ Código de saída: {result.returncode}")
    return result.returncode == 0


def check_coverage():
    """Verifica cobertura atual do EmailService"""
    
    print("🎯 VERIFICADOR DE COBERTURA - SISTEMA DE LEILÃO")
    print("=" * 60)
    
    # 1. Executar testes com cobertura
    success = run_command(
        "pytest tests/test_email_service.py tests/test_email_service_coverage.py -v --cov=services.email_service --cov-report=term-missing --cov-report=html",
        "Executando testes de EmailService com relatório de cobertura"
    )
    
    if not success:
        print("❌ Falha na execução dos testes!")
        return False
    
    # 2. Verificar cobertura específica do email_service
    success = run_command(
        "pytest --cov=services.email_service --cov-report=term-missing --cov-fail-under=95",
        "Verificando se cobertura está acima de 95%"
    )
    
    # 3. Gerar relatório HTML detalhado
    run_command(
        "pytest --cov=services.email_service --cov-report=html:htmlcov_email",
        "Gerando relatório HTML detalhado"
    )
    
    # 4. Mostrar estatísticas finais
    print("\n" + "="*60)
    print("📊 RESUMO DA COBERTURA")
    print("="*60)
    
    if os.path.exists("htmlcov_email"):
        print("✅ Relatório HTML gerado em: htmlcov_email/index.html")
        print("🌐 Para visualizar: abra htmlcov_email/index.html no navegador")
    
    print("\n📋 COMANDOS ÚTEIS:")
    print("1. Ver cobertura geral:")
    print("   pytest --cov=models --cov=services --cov-report=term-missing")
    
    print("\n2. Ver só EmailService:")
    print("   pytest tests/test_email_service*.py --cov=services.email_service --cov-report=term-missing")
    
    print("\n3. Falhar se cobertura < 90%:")
    print("   pytest --cov=services.email_service --cov-fail-under=90")
    
    print("\n4. Relatório HTML completo:")
    print("   pytest --cov=models --cov=services --cov-report=html")
    
    return success


def analyze_missing_lines():
    """Analisa linhas específicas que podem estar faltando"""
    
    print("\n" + "="*60)
    print("🔍 ANÁLISE DE LINHAS NÃO COBERTAS")
    print("="*60)
    
    # Linhas que provavelmente não estão cobertas
    missing_areas = {
        "75-83": "Validação de configuração (múltiplos erros)",
        "92": "Detecção de ambiente CI/CD",
        "146-152": "Tratamento de exceções inesperadas",
        "235-243": "Erros SMTP específicos (SMTPException)",
        "269, 271, 276": "Tratamento de erros gerais em produção",
        "312-336": "Teste de configuração modo produção"
    }
    
    print("🎯 Áreas que precisam de testes:")
    for lines, description in missing_areas.items():
        print(f"   Linhas {lines}: {description}")
    
    print("\n💡 SUGESTÕES DE MELHORIAS:")
    print("1. ✅ Criar test_email_service_coverage.py (arquivo adicional)")
    print("2. ✅ Testar validação com emails inválidos")
    print("3. ✅ Testar detecção de ambiente CI")
    print("4. ✅ Testar exceções SMTP específicas")
    print("5. ✅ Testar configurações de produção")
    print("6. ✅ Testar casos edge (emails vazios, caracteres especiais)")


def create_test_suggestions():
    """Cria sugestões de testes para melhorar cobertura"""
    
    print("\n" + "="*60)
    print("📝 SUGESTÕES DE TESTES ADICIONAIS")
    print("="*60)
    
    suggestions = [
        {
            "area": "Validação de Configuração",
            "tests": [
                "test_email_invalido_sem_arroba()",
                "test_senha_vazia()", 
                "test_multiplos_erros_configuracao()"
            ]
        },
        {
            "area": "Detecção de Ambiente",
            "tests": [
                "test_deteccao_ci_github_actions()",
                "test_deteccao_ci_travis()",
                "test_deteccao_pytest_module()"
            ]
        },
        {
            "area": "Exceções SMTP",
            "tests": [
                "test_smtp_exception_generica()",
                "test_smtp_timeout_error()",
                "test_conexao_recusada()"
            ]
        },
        {
            "area": "Modo Produção",
            "tests": [
                "test_configuracao_producao_invalida()",
                "test_from_field_com_system_name()",
                "test_encoding_utf8()"
            ]
        }
    ]
    
    for suggestion in suggestions:
        print(f"\n🎯 {suggestion['area']}:")
        for test in suggestion['tests']:
            print(f"   ✅ {test}")


def main():
    """Função principal"""
    
    # Verificar se está no diretório correto
    if not os.path.exists("services/email_service.py"):
        print("❌ Execute este script na raiz do projeto (onde está o services/)")
        sys.exit(1)
    
    # Executar verificação de cobertura
    success = check_coverage()
    
    # Analisar linhas faltantes
    analyze_missing_lines()
    
    # Criar sugestões
    create_test_suggestions()
    
    # Resultado final
    print("\n" + "="*60)
    if success:
        print("🎉 COBERTURA VERIFICADA COM SUCESSO!")
        print("📈 Meta: Atingir 95%+ de cobertura no EmailService")
    else:
        print("⚠️  COBERTURA PRECISA SER MELHORADA")
        print("📝 Use os testes sugeridos acima")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Crie o arquivo tests/test_email_service_coverage.py")
    print("2. Adicione os testes sugeridos")
    print("3. Execute: pytest --cov=services.email_service --cov-report=term-missing")
    print("4. Repita até atingir 95%+ de cobertura")
    
    print("\n🏆 OBJETIVO: 100% de cobertura para apresentar ao professor!")


if __name__ == "__main__":
    main()