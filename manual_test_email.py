#!/usr/bin/env python3
"""
Script para testar manualmente o EmailService
Execute: python test_email_manual.py
"""

import sys
import os
from datetime import datetime

# Adicionar path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.email_service import EmailService


def linha_separadora(titulo=""):
    """Imprime linha separadora"""
    print("=" * 70)
    if titulo:
        print(f" {titulo}")
        print("=" * 70)


def testar_deteccao_modo():
    """Testa detecção automática de modo"""
    linha_separadora("TESTE 1: DETECÇÃO AUTOMÁTICA DE MODO")
    
    service = EmailService()
    print(f"Modo detectado: {service.modo}")
    
    config = service.testar_configuracao()
    print(f"Configuração OK: {config['configuracao_ok']}")
    
    print("\nDetalhes da configuração:")
    for detalhe in config['detalhes']:
        print(f"  {detalhe}")
    
    return service


def testar_envio_desenvolvimento():
    """Testa envio em modo desenvolvimento"""
    linha_separadora("TESTE 2: MODO DESENVOLVIMENTO")
    
    service = EmailService(modo='development')
    
    resultado = service.enviar(
        destinatario="vencedor@leilao.com",
        assunto="🎉 Parabéns! Você venceu o leilão!",
        mensagem="""Olá João Silva,

Parabéns! Você venceu o leilão do item 'iPhone 15 Pro' com o lance de R$2.700,00.

Detalhes do leilão:
- Item: iPhone 15 Pro
- Lance vencedor: R$2.700,00
- Data: {data}

Para finalizar a compra, entre em contato conosco em até 48 horas.

Atenciosamente,
Sistema de Leilões""".format(data=datetime.now().strftime("%d/%m/%Y às %H:%M"))
    )
    
    print(f"\nResultado: {resultado['sucesso']}")
    print(f"Modo: {resultado['modo']}")
    
    return service


def testar_envio_teste():
    """Testa envio em modo teste"""
    linha_separadora("TESTE 3: MODO TESTE")
    
    service = EmailService(modo='test')
    
    print("Enviando email de sucesso...")
    resultado1 = service.enviar(
        "vencedor@teste.com",
        "Parabéns! Você venceu!",
        "Esta é uma mensagem de teste que deve ter sucesso."
    )
    
    print(f"Resultado 1: {resultado1['sucesso']} - {resultado1.get('erro', 'OK')}")
    
    print("\nEnviando email que deve falhar...")
    resultado2 = service.enviar(
        "fail@teste.com",
        "Este email deve falhar",
        "Esta mensagem deve gerar uma falha simulada."
    )
    
    print(f"Resultado 2: {resultado2['sucesso']} - {resultado2.get('erro', 'OK')}")
    
    return service


def testar_estatisticas(services):
    """Testa estatísticas de múltiplos serviços"""
    linha_separadora("TESTE 4: ESTATÍSTICAS")
    
    for i, service in enumerate(services, 1):
        stats = service.obter_estatisticas()
        print(f"\nServiço {i} ({service.modo}):")
        print(f"  Emails enviados: {stats['emails_enviados']}")
        print(f"  Emails falharam: {stats['emails_falharam']}")
        print(f"  Total tentativas: {stats['total_tentativas']}")
        print(f"  Taxa de sucesso: {stats['taxa_sucesso']}%")
        print(f"  Configuração válida: {stats['configuracao_valida']}")


def testar_integracao_leilao():
    """Testa integração com sistema de leilão"""
    linha_separadora("TESTE 5: INTEGRAÇÃO COM LEILÃO")
    
    try:
        from models.leilao import Leilao, EstadoLeilao
        from models.participante import Participante
        from models.lance import Lance
        from datetime import timedelta
        
        print("Criando cenário de leilão...")
        
        # Criar participante
        participante = Participante(
            "123.456.789-00", "Maria Vitoriosa",
            "maria@vencedora.com", datetime(1985, 3, 15)
        )
        
        # Criar leilão
        agora = datetime.now()
        leilao = Leilao(
            "MacBook Pro M3 - Teste",
            3000.0,
            agora - timedelta(minutes=1),
            agora + timedelta(minutes=1)
        )
        
        # Simular leilão
        print("Abrindo leilão...")
        leilao.abrir(agora)
        
        print("Adicionando lance...")
        lance = Lance(3500.0, participante, leilao, agora)
        leilao.adicionar_lance(lance)
        
        print("Finalizando leilão (vai tentar enviar email)...")
        leilao.finalizar(agora + timedelta(minutes=2))
        
        print(f"Estado final: {leilao.estado}")
        print(f"Vencedor: {leilao.identificar_vencedor().participante.nome}")
        print(f"Lance vencedor: R${leilao.identificar_vencedor().valor:.2f}")
        
    except ImportError as e:
        print(f"❌ Não foi possível importar módulos do leilão: {e}")
    except Exception as e:
        print(f"❌ Erro durante teste de integração: {e}")


def menu_interativo():
    """Menu interativo para testes"""
    linha_separadora("MENU INTERATIVO DE TESTES")
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Testar detecção automática de modo")
        print("2. Testar modo desenvolvimento")
        print("3. Testar modo teste")
        print("4. Testar todos os modos")
        print("5. Testar integração com leilão")
        print("6. Configurar credenciais de produção")
        print("0. Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "0":
            print("👋 Saindo...")
            break
        elif opcao == "1":
            testar_deteccao_modo()
        elif opcao == "2":
            testar_envio_desenvolvimento()
        elif opcao == "3":
            testar_envio_teste()
        elif opcao == "4":
            services = []
            services.append(testar_deteccao_modo())
            services.append(testar_envio_desenvolvimento())
            services.append(testar_envio_teste())
            testar_estatisticas(services)
        elif opcao == "5":
            testar_integracao_leilao()
        elif opcao == "6":
            configurar_producao()
        else:
            print("❌ Opção inválida!")


def configurar_producao():
    """Ajuda a configurar modo produção"""
    linha_separadora("CONFIGURAÇÃO PARA PRODUÇÃO")
    
    print("Para usar o modo produção, você precisa:")
    print("1. Um email do Gmail")
    print("2. Uma 'Senha de App' (não a senha normal)")
    print("\nPassos para criar senha de app:")
    print("1. Acesse: https://myaccount.google.com/apppasswords")
    print("2. Faça login na sua conta Google")
    print("3. Clique em 'Gerar' e escolha 'App personalizado'")
    print("4. Digite 'Sistema de Leilões' como nome")
    print("5. Copie a senha gerada (16 caracteres)")
    
    print("\nAtualize seu arquivo .env:")
    print("EMAIL_USER=seu.email@gmail.com")
    print("EMAIL_PASSWORD=senha_de_app_de_16_caracteres")
    print("EMAIL_MODE=production")
    
    testar = input("\nDeseja testar a configuração atual? (s/N): ").strip().lower()
    if testar in ['s', 'sim', 'y', 'yes']:
        try:
            service = EmailService(modo='production')
            config = service.testar_configuracao()
            
            print("\nResultado do teste:")
            for detalhe in config['detalhes']:
                print(f"  {detalhe}")
                
            if config['configuracao_ok']:
                print("\n✅ Configuração válida para produção!")
                
                enviar_teste = input("Deseja enviar um email de teste? (s/N): ").strip().lower()
                if enviar_teste in ['s', 'sim', 'y', 'yes']:
                    email_destino = input("Digite o email de destino: ").strip()
                    if email_destino:
                        resultado = service.enviar(
                            email_destino,
                            "🧪 Teste do Sistema de Leilões",
                            f"Este é um email de teste enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}.\n\nSe você recebeu este email, a configuração está funcionando perfeitamente!"
                        )
                        
                        if resultado['sucesso']:
                            print("✅ Email de teste enviado com sucesso!")
                        else:
                            print(f"❌ Falha no envio: {resultado.get('erro', 'Erro desconhecido')}")
            else:
                print("\n❌ Configuração inválida para produção")
                
        except Exception as e:
            print(f"\n❌ Erro ao testar produção: {e}")


def main():
    """Função principal"""
    print("🧪 TESTE MANUAL DO EMAIL SERVICE")
    print("Sistema de Leilões - Teste de Integração de Email")
    
    # Verificar se está em ambiente de desenvolvimento
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Modo automático - roda todos os testes
        services = []
        services.append(testar_deteccao_modo())
        services.append(testar_envio_desenvolvimento())
        services.append(testar_envio_teste())
        testar_estatisticas(services)
        testar_integracao_leilao()
    else:
        # Modo interativo
        menu_interativo()


if __name__ == "__main__":
    main()