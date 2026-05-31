# Relatório de QA - Backend Quizify

**Autor:** Rodrigo Araujo Illydio
**Data:** 29 de Maio de 2026

## 1. Introdução

Este relatório documenta a estratégia de testes de Quality Assurance (QA) desenvolvida para o backend do projeto **Quizify**, uma plataforma de quiz inteligente com geração dinâmica de perguntas via IA. O backend é construído com FastAPI e utiliza a API da OpenAI para gerar os quizzes.

O objetivo principal desta estratégia é garantir a qualidade e a robustez da API, validando os contratos de comunicação com o aplicativo mobile (frontend), ao mesmo tempo em que se minimiza o consumo da API da OpenAI para evitar custos excessivos e limites de requisições (rate limits) durante a fase de testes e apresentação acadêmica.

## 2. Estratégia de Testes

A estratégia de testes foi desenhada com base na análise do código-fonte do backend (`main.py`, `quiz_models.py`, `quiz_service.py`) e na documentação de integração com o frontend (`BACKEND-INTEGRATION.md`, `quiz-api.ts`).

### 2.1. Foco na Validação de Contratos e Regras de Negócio

Os testes priorizam a validação da estrutura das requisições e respostas (contratos) e as regras de negócio implementadas no backend, tais como:

*   **Validação de Entradas:** Garantir que a API rejeite requisições malformadas (ex: padrões de dificuldade inválidos, IDs de questões inexistentes).
*   **Cálculo de Pontuação:** Validar a lógica de pontuação (`/score`), que deve parar de contabilizar pontos no primeiro erro.
*   **Integração com o App:** Focar nos endpoints consumidos diretamente pelo aplicativo mobile (`/quiz/start`, `/quiz/hint`), verificando se eles retornam os dados no formato esperado pelo frontend.

### 2.2. Mitigação do Consumo da OpenAI

Para evitar o consumo excessivo da API da OpenAI, a estratégia adota as seguintes abordagens:

1.  **Testes de Validação (Sem OpenAI):** A maioria dos testes na collection do Postman foca em cenários que não acionam a OpenAI, como:
    *   Health check (`/`).
    *   Cálculo de pontuação (`/score`) com diferentes cenários (acertos, erros, listas vazias, tamanhos incompatíveis).
    *   Validação de payload inválido em `/quiz/start` (ex: padrão de dificuldade incorreto), que deve ser rejeitado antes de chamar a OpenAI.
    *   Solicitação de dica (`/quiz/hint`) com ID inválido, que deve retornar o fallback local sem chamar a OpenAI.
2.  **Avisos Claros na Collection:** Os endpoints que efetivamente chamam a OpenAI (`/generate_quiz`, `/quiz/start` com payload válido, `/quiz/hint` com ID válido, `/help`) foram marcados com avisos claros na descrição da collection do Postman: **"CUIDADO: Este endpoint faz uma chamada à API da OpenAI e pode gerar custos/limites. Use com moderação ou contra um ambiente mockado."**
3.  **Recomendação de Mocking:** Para testes automatizados contínuos (CI/CD), recomenda-se fortemente a implementação de mocks para o serviço da OpenAI (`OpenAIService`), retornando respostas estáticas predefinidas. Isso permite testar a lógica do backend sem qualquer custo ou dependência externa.

## 3. Cobertura de Testes (Collection do Postman)

A collection do Postman (`quizify_backend_postman_collection.json`) foi estruturada nas seguintes pastas:

### 3.1. Status
*   **GET / (Health Check):** Verifica se a API está online e respondendo.

### 3.2. Quiz Generation (Legacy)
*   **GET /generate_quiz:** Testa o endpoint legado de geração de quiz. *Aviso de consumo da OpenAI.*

### 3.3. Quiz Gameplay (App-facing)
*   **POST /quiz/start (OpenAI Call):** Testa a inicialização de um quiz com um padrão válido. *Aviso de consumo da OpenAI.*
*   **POST /quiz/start (Invalid Pattern):** Testa a validação de entrada com um padrão de dificuldade inválido. Espera-se um erro 422 (Unprocessable Entity).
*   **POST /quiz/hint (OpenAI Call):** Testa a solicitação de dica para uma questão válida. *Aviso de consumo da OpenAI.*
*   **POST /quiz/hint (Invalid Question ID):** Testa a solicitação de dica com um ID inválido. Espera-se que retorne uma dica vazia (fallback).

### 3.4. AI Assistant
*   **POST /help (OpenAI Call):** Testa o endpoint de ajuda e explicação. *Aviso de consumo da OpenAI.*

### 3.5. Scoring
*   **POST /score:** Testa o cálculo da pontuação com uma lista de respostas contendo um erro (deve parar de contar no erro).
*   **POST /score (All Correct):** Testa o cálculo com todas as respostas corretas.
*   **POST /score (Empty Answers):** Testa o cálculo com listas vazias.
*   **POST /score (Mismatched Lengths):** Testa a validação quando as listas de respostas e pontos têm tamanhos diferentes. Espera-se um erro 422.

## 4. Conclusão e Próximos Passos

A collection do Postman fornecida oferece uma base sólida para testar manualmente a API do Quizify, cobrindo os principais fluxos e regras de negócio. A estratégia adotada protege o projeto contra custos inesperados da OpenAI durante a fase de testes.

**Próximos Passos Recomendados:**

1.  **Implementar Mocks:** Criar um ambiente de testes (ex: usando `pytest` e `unittest.mock` em Python) onde as chamadas para `OpenAIService` sejam interceptadas e retornem dados estáticos. Isso permitirá a execução de testes automatizados rápidos e gratuitos.
2.  **Completar Endpoints Pendentes:** A documentação do frontend (`CHECKLIST-COMPLEMENTOS.md`) indica que alguns endpoints ainda precisam ser implementados no backend (ex: `/attempts`, `/ranking`). A collection do Postman deve ser atualizada assim que esses endpoints estiverem disponíveis.
3.  **Testes de Carga (Opcional):** Se o projeto for escalado, realizar testes de carga (ex: com Locust ou k6) em um ambiente mockado para avaliar o desempenho do FastAPI sob estresse.
