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
