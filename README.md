# 🏆 Sistema de Leilões com Banco de Dados

Este é um projeto de sistema de controle de leilões, desenvolvido como parte de um trabalho acadêmico. O objetivo principal é implementar as funcionalidades de cadastro e controle de leilões com **testes unitários e de integração cobrindo 100% do código**, utilizando um banco de dados **SQLite** para persistência de dados.

---

## 📌 Funcionalidades Implementadas

- ✅ **Gestão de Participantes**: Cadastro com validação rigorosa de CPF e e-mail
- ✅ **Controle de Leilões**: Estados automáticos (INATIVO → ABERTO → FINALIZADO/EXPIRADO)
- ✅ **Sistema de Lances**: Validação de valores mínimos e lances consecutivos
- ✅ **Filtros Avançados**: Busca por estado, data e período específico
- ✅ **Notificações Inteligentes**: Serviço de e-mail com múltiplos modos de operação
- ✅ **Gerenciamento Completo**: Edição e remoção seguindo regras de negócio
- ✅ **Persistência de Dados**: Utilização de SQLite com SQLAlchemy
- ✅ **Cobertura de Testes**: Unitários, de integração e E2E com 100% de cobertura
- ✅ **Testes E2E**: Cenários de ponta-a-ponta com BDD (pytest-bdd)

---

## 🗂️ Estrutura do Projeto

```
Sistema de Leilões/
├── models/
│   ├── base.py                     # Base para os modelos do SQLAlchemy
│   ├── database.py                 # Configuração do banco de dados
│   ├── lance.py                    # Classe Lance com valor e participante
│   ├── leilao.py                   # Classe Leilao e enum EstadoLeilao
│   ├── participante.py             # Classe Participante com validações
│   └── gerenciador_leiloes.py      # Gerenciador principal do sistema
│
├── services/
│   └── email_service.py            # Serviço de e-mail inteligente
│
├── tests/
│   ├── e2e/                        # Testes End-to-End (BDD)
│   │   ├── gerenciamento_leilao.feature
│   │   └── test_leilao_e2e.py
│   ├── integration/                # Testes de Integração
│   │   ├── test_gerenciador_leiloes.py
│   │   ├── test_gerenciador_leiloes_coverage.py
│   │   └── test_integration.py
│   ├── unit/                       # Testes Unitários
│   │   ├── test_database.py
│   │   ├── test_detectar_modo.py
│   │   ├── test_email_service.py
│   │   ├── test_lance.py
│   │   ├── test_leilao.py
│   │   ├── test_main_block.py
│   │   ├── test_models_coverage.py
│   │   └── test_participante.py
│   └── conftest.py                 # Configurações globais para os testes
│
├── .env                           # Configurações do ambiente
├── .gitignore                     # Arquivos ignorados pelo Git
├── leilao.db                      # Banco de dados SQLite
├── README.md                      # Documentação do projeto
└── requirements.txt               # Arquivo de instalação das dependencias
```

---

## 🔧 Configuração do Ambiente (.env)

O sistema utiliza um arquivo `.env` para configurar diferentes aspectos da aplicação, especialmente o serviço de e-mail que possui **múltiplos modos de operação**:

### 📧 Configurações de E-mail

```bash
# =============================================================================
# CONFIGURAÇÕES DE EMAIL
# =============================================================================

# Credenciais do Gmail (para modo PRODUÇÃO)
EMAIL_USER=seu.email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app_aqui

# Servidor SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Modo de operação do sistema de e-mail
EMAIL_MODE=test  # production | development | test | auto
```

### 🎯 Modos de Operação do E-mail

| Modo | Descrição | Uso Recomendado |
|------|-----------|-----------------|
| **`production`** | Envia e-mails reais via SMTP | Ambiente de produção |
| **`development`** | Apenas loga e-mails no console | Desenvolvimento local |
| **`test`** | Simula envio para testes automatizados | Execução de testes |
| **`auto`** | Detecta automaticamente o melhor modo | Configuração inteligente |

### ⚙️ Outras Configurações

```bash
# Sistema
SYSTEM_NAME=Sistema de Leilões
DEBUG_EMAIL=true
TIMEZONE=America/Sao_Paulo

# Testes
TEST_EMAIL=teste@exemplo.com
TEST_SIMULATE_EMAIL_FAILURES=false
```

### 🔐 Configuração do Gmail

Para usar o modo `production` com Gmail:

1. Ative a **Verificação em 2 etapas** na sua conta Google
2. Gere uma **Senha de App** em: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use essa senha no `EMAIL_PASSWORD` (não a senha normal da conta)

---

## 🧪 Sistema de Testes

O projeto implementa uma **estratégia de testes abrangente** com duas camadas:

### 📋 Testes Unitários (`tests/unit/`)
- **Foco**: Testam classes e funções de forma isolada.
- **Cobertura**: Cada método e regra de negócio.
- **Validações**: CPF, e-mail, estados, transições.
- **Exceções**: Todos os cenários de erro mapeados.

### 🔗 Testes de Integração (`tests/integration/`)
- **Foco**: Testam a interação entre múltiplos componentes do sistema.
- **Fluxos**: Cenários completos de leilão, envolvendo gerenciador e banco de dados.
- **Serviços**: Integração com o `EmailService`.
- **Persistência**: Gerenciamento de dados em memória.

### 🧪 Testes End-to-End (E2E) (`tests/e2e/`)
- **Foco**: Simulam um fluxo de usuário completo, do início ao fim.
- **Tecnologia**: `pytest-bdd` para escrever cenários em linguagem natural (Gherkin).
- **Validação**: Garante que a integração de todos os componentes funciona como esperado em um caso de uso real.

### 🎯 Cenários de Teste Cobertos

**Participantes:**
- ✅ Validação de CPF no formato correto (123.456.789-00)
- ✅ Validação de e-mail com formato válido
- ✅ Prevenção de remoção quando há lances associados

**Leilões:**
- ✅ Transições de estado respeitando regras temporais
- ✅ Abertura apenas após data de início
- ✅ Finalização automática com envio de e-mail
- ✅ Expiração quando não há lances

**Lances:**
- ✅ Validação de valor mínimo
- ✅ Incremento obrigatório sobre lance anterior
- ✅ Prevenção de lances consecutivos do mesmo participante

**Gerenciamento:**
- ✅ Filtros por estado e período
- ✅ Edição apenas de leilões inativos
- ✅ Remoção seguindo regras de integridade

---

## 🚀 Como Executar

### 1️⃣ Configuração Inicial
```bash
# Clone o repositório
git clone https://github.com/vitimrcosta/Sistema_Leilao_BC.git
cd Sistema_Leilao_BC

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### 2️⃣ Configuração do Ambiente
```bash
# Crie o arquivo .env na raiz do projeto
# (opcional, para configurar o serviço de e-mail)

# Crie o banco de dados
python -c "from models.database import create_db_tables; create_db_tables()"
```

### 3️⃣ Executando os Testes

```bash
# Todos os testes com relatório detalhado
pytest -v

# Apenas testes unitários
pytest tests/unit/ -v

# Apenas testes de integração
pytest tests/integration/ -v

# Apenas testes E2E
pytest tests/e2e/ -v

# Com relatório de cobertura
pytest --cov=models --cov=services --cov-report=term-missing

# Teste específico
pytest tests/test_leilao.py::test_abrir_leilao_ja_aberto -v
```

### 4️⃣ Verificando Cobertura
```bash
# Relatório detalhado de cobertura
pytest --cov=models --cov=services --cov-report=html

# Abre relatório HTML no navegador
# Arquivo gerado em: htmlcov/index.html
```

---

## 🏗️ Arquitetura do Sistema

### 📦 Modelos de Domínio
- **`Lance`**: Valor, participante, leilão e timestamp
- **`Participante`**: CPF, nome, e-mail com validações
- **`Leilao`**: Estados, datas, lances e regras de transição
- **`GerenciadorLeiloes`**: Operações CRUD e filtros

### 🔧 Serviços
- **`EmailService`**: Sistema inteligente de notificações
  - Detecção automática de ambiente
  - Múltiplos modos de operação
  - Tratamento robusto de erros
  - Logs detalhados para debug

### 🗄️ Banco de Dados
- **`SQLAlchemy`**: ORM para mapeamento objeto-relacional
- **`SQLite`**: Banco de dados leve e sem servidor
- **`Session`**: Gerenciamento de transações

### 📊 Estados do Leilão
```
INATIVO → ABERTO → FINALIZADO
    ↓         ↓
    ✗      EXPIRADO
```

---

## 🎯 Destaques Técnicos

### 🛡️ Validações Robustas
- **Regex para CPF**: Formato brasileiro obrigatório
- **Regex para E-mail**: Validação básica de estrutura
- **Datas**: Prevenção de períodos inválidos

### 🔄 Tratamento de Exceções
- **ValueError**: Para regras de negócio violadas
- **Estados Inválidos**: Transições não permitidas
- **Dados Inconsistentes**: Validação na entrada

### 📈 Facilidade de Teste
- **Mocks**: Para isolamento de dependências
- **Fixtures**: Dados padronizados para testes
- **Parametrização**: Múltiplos cenários automatizados

---

## 🎓 Objetivo Acadêmico

Este sistema foi desenvolvido para demonstrar:

- **Programação Orientada a Objetos**: Classes bem estruturadas
- **Testes Automatizados**: Cobertura completa e estratégias diferenciadas
- **Tratamento de Exceções**: Validações robustas
- **Separação de Responsabilidades**: Arquitetura limpa
- **Boas Práticas**: Código limpo e documentado

---

## 👥 Equipe de Desenvolvimento

Desenvolvido por **Victor, Roberta e Luiz**.

📧 Para dúvidas ou sugestões: **victor.rcosta@outlook.com**

---

## 🔒 Importante

- **Nunca** commite o arquivo `.env` com credenciais reais
- Use **Senhas de App** para Gmail, não a senha da conta
- Em **desenvolvimento**, use `EMAIL_MODE=development` para apenas logar e-mails
- Os **testes** executam em modo simulação automaticamente