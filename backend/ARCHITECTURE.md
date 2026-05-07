# Arquitetura do Backend — Quizify

## Visão geral

A API segue uma arquitetura em camadas simples com três responsabilidades bem separadas:

```
Requisição HTTP
      ↓
  main.py          ← camada de rotas (recebe, valida, responde)
      ↓
  quiz_service.py  ← camada de lógica (regras de negócio)
      ↓
  openai_service.py ← camada de integração (fala com a OpenAI)
```

Os modelos em `quiz_models.py` definem o contrato de dados entre todas as camadas — o que entra e o que sai de cada endpoint.

---

## Estrutura de arquivos

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── quiz_models.py
│   └── services/
│       ├── __init__.py
│       ├── openai_service.py
│       └── quiz_service.py
├── testes/
│   └── teste_quiz_api.py
├── .env
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

---

## O que cada arquivo faz

### `app/main.py`
Entrypoint da API. Define as rotas HTTP e conecta cada endpoint ao serviço correspondente.

Responsabilidades:
- Declarar os endpoints (`GET /`, `GET /generate_quiz`, `POST /help`, `POST /score`)
- Receber e validar os dados de entrada via Pydantic (automático pelo FastAPI)
- Chamar o `QuizService` e retornar a resposta
- Tratar erros e retornar HTTP 500 com mensagem legível

Não contém lógica de negócio — só roteia.

---

### `app/models/quiz_models.py`
Define todos os schemas de dados da aplicação usando Pydantic.

Modelos presentes:

| Modelo | Uso |
|---|---|
| `QuestionOption` | Uma opção de resposta (`text` + `is_correct`) |
| `GeneratedQuestion` | Uma pergunta completa com opções, dificuldade, pontos e explicação |
| `QuizResponse` | Resposta do `/generate_quiz` — lista de perguntas + total de pontos |
| `HelpRequest` | Body do `/help` — pergunta e opções |
| `HelpResponse` | Resposta do `/help` — dica e explicação |
| `ScoreRequest` | Body do `/score` — array de respostas e pontos por pergunta |
| `ScoreResponse` | Resposta do `/score` — pontuação final |

Também define a constante `POINTS_BY_DIFFICULTY` que mapeia dificuldade → pontos:

```python
POINTS_BY_DIFFICULTY = {
    "fácil": 10,
    "média": 20,
    "difícil": 30,
}
```

---

### `app/services/openai_service.py`
Camada de integração com a OpenAI. Isola tudo que é específico da API externa.

Responsabilidades:
- Carregar a `OPENAI_API_KEY` do `.env`
- Instanciar o cliente da OpenAI
- Expor um método genérico `generate_chat_completion(system_prompt, user_prompt)` que:
  - Chama o modelo `gpt-4.1-mini`
  - Força resposta em formato JSON (`response_format: json_object`)
  - Retorna o JSON já parseado como dicionário Python

O motivo de isolar aqui é simples: se quiser trocar de modelo, mudar para outro provedor (Anthropic, Gemini, etc.) ou ajustar parâmetros como `temperature`, você mexe só neste arquivo.

---

### `app/services/quiz_service.py`
Camada de lógica de negócio. É o coração da aplicação.

Contém três métodos:

**`generate_quiz()`**
- Monta os prompts (system + user) instruindo a OpenAI a gerar 12 perguntas de tecnologia (4 fáceis, 4 médias, 4 difíceis)
- Recebe o JSON da OpenAI e mapeia para os modelos Pydantic
- Atribui a pontuação de cada pergunta com base na dificuldade via `POINTS_BY_DIFFICULTY`
- Gera um `quiz_id` único com `uuid4()`
- Retorna um `QuizResponse` completo

**`get_help(question, options)`**
- Monta um prompt pedindo uma dica sutil e uma explicação educativa
- Retorna `HelpResponse` com `hint` e `explanation`

**`calculate_score(answers, points_per_question)`**
- Percorre o array de respostas em ordem
- Acumula pontos enquanto o jogador acerta
- Para imediatamente ao primeiro erro
- Retorna score, total de acertos e total de perguntas respondidas

---

### `app/services/openai_service.py` — parâmetros do modelo

```python
model="gpt-4.1-mini"   # modelo usado
temperature=0.7         # criatividade das perguntas (0 = determinístico, 1 = mais criativo)
response_format="json_object"  # força saída em JSON válido
```

---

## Fluxo completo de uma partida

```
Frontend                          Backend                        OpenAI
   |                                 |                              |
   |--- GET /generate_quiz --------> |                              |
   |                                 |--- chat.completions.create ->|
   |                                 |<-- JSON com 12 perguntas ----|
   |<-- QuizResponse ----------------|                              |
   |                                 |                              |
   | (usuário joga...)               |                              |
   |                                 |                              |
   | (opcional) POST /help --------> |                              |
   |                                 |--- chat.completions.create ->|
   |<-- HelpResponse ----------------|                              |
   |                                 |                              |
   |--- POST /score ---------------> |                              |
   |    { answers, points }          | (cálculo local, sem IA)      |
   |<-- ScoreResponse ---------------|                              |
```

O `/score` não chama a OpenAI — é cálculo puro no servidor, rápido e sem custo.

---

## Como mexer

### Trocar o modelo da OpenAI
Em `app/services/openai_service.py`, linha:
```python
model="gpt-4.1-mini"
```
Troque por `gpt-4o`, `gpt-3.5-turbo`, etc.

---

### Mudar a quantidade de perguntas ou distribuição de dificuldade
Em `app/services/quiz_service.py`, no `user_prompt` do método `generate_quiz()`:
```
- 4 perguntas de dificuldade 'fácil'
- 4 perguntas de dificuldade 'média'
- 4 perguntas de dificuldade 'difícil'
```
Ajuste os números como quiser. Lembre de atualizar o README com o novo total de pontos.

---

### Mudar a pontuação por dificuldade
Em `app/models/quiz_models.py`:
```python
POINTS_BY_DIFFICULTY = {
    "fácil": 10,
    "média": 20,
    "difícil": 30,
}
```
Altere os valores. A pontuação máxima é calculada automaticamente.

---

### Mudar os subtemas de tecnologia
Em `app/services/quiz_service.py`, no `system_prompt` e `user_prompt` do `generate_quiz()`:
```python
"Crie perguntas variadas cobrindo: linguagens de programação, frameworks, IDEs, ..."
```
Adicione ou remova subtemas conforme necessário.

---

### Mudar a lógica de pontuação (ex: não parar ao errar)
Em `app/services/quiz_service.py`, método `calculate_score()`:
```python
for answered_correct, points in zip(answers, points_per_question):
    if answered_correct:
        score += points
    else:
        break  # remova esta linha para somar só os acertos sem parar
```

---

### Adicionar um novo endpoint
1. Crie o schema de request/response em `quiz_models.py`
2. Implemente a lógica em `quiz_service.py`
3. Registre a rota em `main.py`

---

## Dependências

| Pacote | Versão | Uso |
|---|---|---|
| fastapi | 0.110.0 | Framework web |
| uvicorn | 0.28.0 | Servidor ASGI |
| pydantic | 2.6.1 | Validação de dados |
| openai | 1.13.3 | SDK da OpenAI |
| python-dotenv | 1.0.1 | Leitura do `.env` |
