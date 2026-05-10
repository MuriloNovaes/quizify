# 🏗️ Arquitetura do Backend — Quizify

> Documentação técnica da API. Explica como cada peça funciona, como se conectam e como mexer sem quebrar nada.

---

## 📐 Visão Geral

A API segue uma **arquitetura em camadas** com três níveis bem separados. Cada camada tem uma única responsabilidade:

```
┌─────────────────────────────────────────┐
│           Requisição HTTP               │
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│             main.py                     │
│         🔀 Camada de Rotas              │
│  Recebe, valida e responde requisições  │
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│           quiz_service.py               │
│        ⚙️ Camada de Negócio             │
│   Lógica do quiz, ajuda e pontuação     │
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│          openai_service.py              │
│       🤖 Camada de Integração           │
│       Comunicação com a OpenAI          │
└─────────────────────────────────────────┘
```

Os **modelos** em `quiz_models.py` definem o contrato de dados entre todas as camadas — o que entra e o que sai de cada endpoint.

---

## 📁 Estrutura de Arquivos

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   ← rotas HTTP
│   ├── models/
│   │   ├── __init__.py
│   │   └── quiz_models.py        ← schemas de dados
│   └── services/
│       ├── __init__.py
│       ├── openai_service.py     ← integração OpenAI
│       └── quiz_service.py       ← lógica de negócio
├── testes/
│   └── teste_quiz_api.py
├── .env                          ← 🔒 não sobe pro git
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

---

## 🔍 O Que Cada Arquivo Faz

### `app/main.py` — Rotas HTTP

Entrypoint da API. Define os endpoints e conecta cada rota ao serviço.

**Responsabilidades:**
- Declarar as rotas (`GET /`, `GET /generate_quiz`, `POST /help`, `POST /score`)
- Validar dados de entrada automaticamente via Pydantic + FastAPI
- Delegar a lógica para o `QuizService`
- Capturar erros e retornar HTTP 500 com mensagem legível

> ⚠️ Não contém lógica de negócio — só roteia.

---

### `app/models/quiz_models.py` — Schemas de Dados

Define todos os contratos de entrada e saída da API usando **Pydantic**.

| Modelo | Direção | Descrição |
|---|---|---|
| `QuestionOption` | interno | Uma opção de resposta (`text` + `is_correct`) |
| `GeneratedQuestion` | interno | Pergunta completa com opções, dificuldade, pontos e explicação |
| `QuizResponse` | saída | Resposta do `/generate_quiz` |
| `HelpRequest` | entrada | Body do `/help` |
| `HelpResponse` | saída | Resposta do `/help` |
| `ScoreRequest` | entrada | Body do `/score` |
| `ScoreResponse` | saída | Resposta do `/score` |

Também define a tabela de pontuação:

```python
POINTS_BY_DIFFICULTY = {
    "fácil":   10,
    "média":   20,
    "difícil": 30,
}
```

---

### `app/services/openai_service.py` — Integração OpenAI

Isola tudo que é específico da API externa. O resto da aplicação não sabe que existe uma IA por baixo.

**O que faz:**
- Carrega a `OPENAI_API_KEY` do `.env`
- Instancia o cliente da OpenAI
- Expõe um único método `generate_chat_completion(system_prompt, user_prompt)` que:
  - Chama o modelo `gpt-4.1-mini`
  - Força resposta em JSON válido (`response_format: json_object`)
  - Retorna o JSON já parseado como dicionário Python

**Parâmetros configuráveis:**

```python
model       = "gpt-4.1-mini"  # modelo usado
temperature = 0.7              # criatividade (0 = fixo, 1 = mais criativo)
```

> 💡 Se quiser trocar de modelo ou provedor, mexa **só aqui**.

---

### `app/services/quiz_service.py` — Lógica de Negócio

O coração da aplicação. Contém três métodos:

#### `generate_quiz()`
```
1. Monta system_prompt + user_prompt instruindo a IA
2. Chama openai_service.generate_chat_completion()
3. Mapeia o JSON retornado para modelos Pydantic
4. Atribui pontuação por dificuldade via POINTS_BY_DIFFICULTY
5. Gera um quiz_id único com uuid4()
6. Retorna QuizResponse completo
```

#### `get_help(question, options)`
```
1. Monta prompt pedindo dica sutil + explicação educativa
2. Chama openai_service.generate_chat_completion()
3. Retorna HelpResponse com hint e explanation
```

#### `calculate_score(answers, points_per_question)`
```
1. Percorre o array de respostas em ordem
2. Acumula pontos enquanto o jogador acerta
3. Para imediatamente ao primeiro erro
4. Retorna score, acertos e total de perguntas
```

> 🔑 O `/score` **não chama a OpenAI** — é cálculo puro no servidor, sem custo e sem latência.

---

## 🔄 Fluxo Completo de uma Partida

```
Frontend                    Backend                      OpenAI
   │                           │                            │
   │── GET /generate_quiz ───► │                            │
   │                           │── chat.completions ──────► │
   │                           │◄── 12 perguntas em JSON ── │
   │◄── QuizResponse ───────── │                            │
   │                           │                            │
   │   (usuário responde...)   │                            │
   │                           │                            │
   │── POST /help (opcional) ► │                            │
   │                           │── chat.completions ──────► │
   │◄── HelpResponse ───────── │◄── dica + explicação ───── │
   │                           │                            │
   │── POST /score ──────────► │                            │
   │   { answers, points }     │  (cálculo local, sem IA)   │
   │◄── ScoreResponse ───────── │                            │
```

---

## 🛠️ Como Mexer

### 🔁 Trocar o modelo da OpenAI
`app/services/openai_service.py`
```python
# antes
model="gpt-4.1-mini"

# depois (exemplos)
model="gpt-4o"
model="gpt-3.5-turbo"
```

---

### 📊 Mudar a pontuação por dificuldade
`app/models/quiz_models.py`
```python
POINTS_BY_DIFFICULTY = {
    "fácil":   10,   # ← altere aqui
    "média":   20,
    "difícil": 30,
}
```
A pontuação máxima é calculada automaticamente — não precisa mexer em mais nada.

---

### 🔢 Mudar a quantidade ou distribuição de perguntas
`app/services/quiz_service.py` → método `generate_quiz()` → `user_prompt`
```
- 4 perguntas de dificuldade 'fácil'    ← altere aqui
- 4 perguntas de dificuldade 'média'
- 4 perguntas de dificuldade 'difícil'
```

---

### 🎯 Mudar os subtemas de tecnologia
`app/services/quiz_service.py` → `system_prompt` e `user_prompt`
```python
"Crie perguntas variadas cobrindo: linguagens de programação, frameworks, IDEs, ..."
#                                  ↑ adicione ou remova subtemas aqui
```

---

### 🏆 Mudar a lógica de pontuação
`app/services/quiz_service.py` → método `calculate_score()`

```python
# comportamento atual: para ao errar
for answered_correct, points in zip(answers, points_per_question):
    if answered_correct:
        score += points
    else:
        break  # ← remova para somar só os acertos sem parar

# alternativa: somar todos os acertos independente de erros
score = sum(p for a, p in zip(answers, points_per_question) if a)
```

---

### ➕ Adicionar um novo endpoint
1. Crie os schemas em `quiz_models.py`
2. Implemente a lógica em `quiz_service.py`
3. Registre a rota em `main.py`

---

## 📦 Dependências

| Pacote | Versão | Função |
|---|---|---|
| `fastapi` | 0.110.0 | Framework web |
| `uvicorn` | 0.28.0 | Servidor ASGI |
| `pydantic` | 2.6.1 | Validação de dados |
| `openai` | 1.13.3 | SDK da OpenAI |
| `python-dotenv` | 1.0.1 | Leitura do `.env` |
