# 🕹️ Sistema de Leilões

Este é um projeto de sistema de controle de leilões, desenvolvido como parte de um trabalho acadêmico. O objetivo principal é implementar as funcionalidades de cadastro e controle de leilões, com **testes unitários cobrindo 100% do código**.

---

## 📌 Funcionalidades Implementadas

- [x] Cadastro de leilões com nome, lance mínimo, data de início e término
- [x] Controle de estados do leilão: `INATIVO`, `ABERTO`, `FINALIZADO`, `EXPIRADO`
- [x] Regras de transição entre estados validadas via exceções
- [x] Registro e validação de lances (respeitando o valor mínimo)
- [x] Cadastro e validação de participantes (CPF e e-mail)
- [x] Gerenciador de leilões com filtros por estado e data
- [x] Proibição de remoção de participantes com lances ativos
- [x] Simulação de envio de e-mails via serviço fictício
- [x] Testes unitários para todos os módulos

---

## 🗂️ Estrutura do Projeto

models/
├── participante.py
├── leilao.py
├── lance.py
├── gerenciador_leiloes.py
services/
└── email_service.py
tests/
├── test_participante.py
├── test_leilao.py
├── test_lance.py
├── test_gerenciador_leiloes.py
└── test_email_service.py

## 🧪 Testes

Os testes foram escritos com [Pytest](https://docs.pytest.org/) e cobrem os seguintes cenários:

- Validação de CPF e e-mail de participantes
- Criação de leilão com estado `INATIVO`
- Abertura e encerramento de leilões de acordo com regras de data
- Registro de lances válidos e rejeição de lances abaixo do mínimo
- Listagem de leilões por estado e por intervalo de datas
- Proibição de remoção de participantes com lances existentes
- Envio simulado de e-mail e verificação de saída via `capsys`

### 🔧 Rodando os testes

1. Ative seu ambiente virtual (fora da pasta do projeto):
   ```bash
   venv_leilao\Scripts\activate  # Windows
   source venv_leilao/bin/activate  # Linux/macOS
   pytest

## 📎 Requisitos

- Python 3.10+

- Pytest

   ```bash
   pip install pytest

## 🎓 Objetivo Acadêmico

Este sistema foi desenvolvido com o propósito de aplicar e demonstrar:

- Princípios de programação orientada a objetos
- Tratamento de exceções
- Boas práticas com testes unitários automatizados
- Separação de responsabilidades entre entidades, serviços e regras de negócio

## 👨‍💻 Autor

Desenvolvido por Victor, Roberta, Luiz.
Para dúvidas ou sugestões, envie um e-mail para victor.rcosta@outlook.com.

