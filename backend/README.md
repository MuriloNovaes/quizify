# Backend — Quizify API

API REST construída com **FastAPI** + **OpenAI** que gera quizzes de tecnologia com pontuação progressiva por dificuldade.

---

## Estrutura

```
backend/
├── app/
│   ├── main.py                  # Entrypoint da API
│   ├── models/
│   │   └── quiz_models.py       # Schemas de request/response
│   └── services/
│       ├── openai_service.py    # Integração com a OpenAI
│       └── quiz_service.py      # Lógica do quiz, ajuda e pontuação
├── testes/
│   └── teste_quiz_api.py
├── .env                         # Variáveis de ambiente (não subir no git)
├── requirements.txt
└── README.md
```

---

## Instalação e configuração

```bash
cd backend
pip install -r requirements.txt
```

Crie o arquivo `.env`:

```env
OPENAI_API_KEY=sk-proj-...
```

---

## Rodando localmente

```bash
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger (teste interativo): `http://localhost:8000/docs`

---

## Expondo com ngrok

```bash
ngrok http 8000
```

Use a URL gerada (`https://xxxx.ngrok-free.app`) como `BASE_URL` no frontend web ou mobile.

> A API já está configurada com **CORS aberto** (`allow_origins=["*"]`), então tanto React Native quanto aplicações web conseguem consumir sem bloqueios. Em produção, restrinja para o domínio do seu frontend.

---

## Pontuação por dificuldade

| Dificuldade | Pontos |
|-------------|--------|
| Fácil       | 10     |
| Média       | 20     |
| Difícil     | 30     |

Pontuação máxima por partida: **240 pontos** (4×10 + 4×20 + 4×30)

---

## Endpoints

### `GET /`
Healthcheck — use para verificar se a API está no ar.

```json
{ "message": "API Quiz de Tecnologia no ar!" }
```

---

### `GET /generate_quiz`
Gera 12 perguntas de tecnologia: 4 fáceis, 4 médias e 4 difíceis.

Subtemas: linguagens de programação, frameworks, IDEs, estruturas de dados, algoritmos, banco de dados, backend, frontend e dados.

**Resposta:**
```json
{
  "quiz_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "questions": [
    {
      "question": "Qual estrutura de dados usa FIFO?",
      "options": [
        { "text": "Pilha", "is_correct": false },
        { "text": "Fila", "is_correct": true },
        { "text": "Árvore", "is_correct": false },
        { "text": "Grafo", "is_correct": false }
      ],
      "difficulty": "fácil",
      "points": 10,
      "explanation": "Fila segue FIFO: primeiro a entrar, primeiro a sair."
    }
  ],
  "total_possible_points": 240
}
```

> Salve `quiz_id` e `points` de cada pergunta no estado do app — você vai precisar para calcular o score.

---

### `POST /help`
Retorna uma dica para uma pergunta sem revelar a resposta. Use quando o usuário pedir ajuda.

**Body:**
```json
{
  "question": "Qual estrutura de dados usa FIFO?",
  "options": ["Pilha", "Fila", "Árvore", "Grafo"]
}
```

**Resposta:**
```json
{
  "hint": "Pense em uma fila de banco — quem chega primeiro é atendido primeiro.",
  "explanation": "Estruturas FIFO são usadas em filas de processamento, como filas de mensagens e buffers."
}
```

---

### `POST /score`
Calcula a pontuação da partida. A lógica é:
- Acumulou pontos enquanto acertava
- **Para ao primeiro erro** e retorna o que foi acumulado até ali
- Se acertar todas, retorna o total

**Body:**
```json
{
  "answers": [true, true, false, true],
  "points_per_question": [10, 10, 20, 20]
}
```

**Resposta:**
```json
{
  "score": 20,
  "total_possible": 60,
  "correct": 2,
  "total": 4
}
```

> `answers` deve seguir a mesma ordem das perguntas retornadas pelo `/generate_quiz`.
> `points_per_question` é o array de `points` de cada pergunta na mesma ordem.

---

---

## Fluxo de integração (React Native / Web)

```
1. GET /generate_quiz
   → salva questions[] e total_possible_points no estado

2. Exibe perguntas uma a uma
   → usuário seleciona uma opção
   → registra true/false em answers[]

3. Ao errar OU terminar todas as perguntas:
   POST /score com { answers, points_per_question }
   → exibe tela de resultado com score e correct

4. (Opcional) Botão de dica durante a partida:
   POST /help com { question, options }
   → exibe hint e explanation em modal
```

---

## .gitignore recomendado

```
.env
__pycache__/
*.pyc
.venv/
```
