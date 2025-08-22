# tests/e2e/gerenciamento_leilao.feature
Feature: Gerenciamento de um Leilão Completo

  Scenario: Um participante dá um lance vencedor em um leilão
    Given um leilão chamado "Notebook Gamer" está cadastrado com lance mínimo de 2500.0
    And um participante chamado "Carlos" está cadastrado
    When o leilão "Notebook Gamer" é aberto
    And "Carlos" dá um lance de 2600.0 no leilão "Notebook Gamer"
    And o leilão "Notebook Gamer" é finalizado
    Then o vencedor do leilão "Notebook Gamer" deve ser "Carlos"
    And o valor do lance vencedor deve ser 2600.0

  Scenario: Lance abaixo do valor mínimo
    Given um leilão chamado "Smartphone" está cadastrado com lance mínimo de 1000.0
    And um participante chamado "Ana" está cadastrado
    When o leilão "Smartphone" é aberto
    And "Ana" tenta dar um lance de 900.0 no leilão "Smartphone"
    And o leilão "Smartphone" é finalizado
    Then o leilão "Smartphone" não deve ter vencedor

  Scenario: Múltiplos participantes e lances
    Given um leilão chamado "Tablet" está cadastrado com lance mínimo de 1500.0
    And um participante chamado "Carlos" está cadastrado
    And um participante chamado "Beatriz" está cadastrado
    When o leilão "Tablet" é aberto
    And "Carlos" dá um lance de 1600.0 no leilão "Tablet"
    And "Beatriz" dá um lance de 1700.0 no leilão "Tablet"
    And o leilão "Tablet" é finalizado
    Then o vencedor do leilão "Tablet" deve ser "Beatriz"
    And o valor do lance vencedor deve ser 1700.0

  Scenario: Leilão sem lances
    Given um leilão chamado "Cadeira Gamer" está cadastrado com lance mínimo de 700.0
    When o leilão "Cadeira Gamer" é aberto
    And o leilão "Cadeira Gamer" é finalizado
    Then o leilão "Cadeira Gamer" não deve ter vencedor

  Scenario: Lance após o leilão ser finalizado
    Given um leilão chamado "Monitor Ultrawide" está cadastrado com lance mínimo de 1800.0
    And um participante chamado "Daniel" está cadastrado
    When o leilão "Monitor Ultrawide" é aberto
    And o leilão "Monitor Ultrawide" é finalizado
    And "Daniel" tenta dar um lance de 1900.0 no leilão "Monitor Ultrawide"
    Then o leilão "Monitor Ultrawide" não deve ter vencedor
