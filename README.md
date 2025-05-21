# 🕹️ Sistema de Leilões

Este é um projeto de sistema de controle de leilões, desenvolvido como parte de um trabalho acadêmico. O objetivo principal é implementar as funcionalidades de cadastro e controle de leilões, com **testes unitários cobrindo 100% do código**.

> ⚠️ **Status**: Em desenvolvimento. Até o momento, foi implementada a parte de cadastro e controle de estado dos leilões.

---

## 📌 Funcionalidades Implementadas

- [x] Cadastro de leilões com nome, lance mínimo, data de início e término
- [x] Controle de estados do leilão: `INATIVO`, `ABERTO`, `FINALIZADO`, `EXPIRADO`
- [x] Regras de transição entre estados validadas via exceções
- [x] Testes unitários para cobrir o comportamento do leilão

---

## 🧪 Testes

Os testes foram escritos com [Pytest](https://docs.pytest.org/) e cobrem os seguintes cenários:

- Criação de leilão com estado `INATIVO`
- Tentativa de abrir leilão antes da data de início (erro esperado)
- Finalização de leilão sem lances (estado `EXPIRADO`)

### 🔧 Rodando os testes

1. Ative seu ambiente virtual (fora da pasta do projeto):
   ```bash
   venv_leilao\Scripts\activate
