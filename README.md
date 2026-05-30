# 🎯 Quizify

> Plataforma de quiz inteligente com geração dinâmica de perguntas via IA. Projeto acadêmico full stack mobile.

---

## 👥 Equipe

| Nome | GitHub |
|---|---|
| Murilo Barbosa Novaes | [@MuriloNovaes](https://github.com/MuriloNovaes) |
| Kauã Santos Simplicio | [@KauaSimplicioDEV](https://github.com/KauaSimplicioDEV) |
| Rodrigo Illydio | [@digoexec](https://github.com/digoexec) | 

---

## 📱 Sobre o Projeto

O Quizify é uma aplicação mobile que gera quizzes de tecnologia em tempo real usando inteligência artificial. O jogador responde perguntas de múltipla escolha com dificuldades progressivas e acumula pontos enquanto acerta — ao errar, a partida encerra e a pontuação é registrada.

---

## 🗂️ Estrutura do Repositório

```
quizify/
├── backend/    ← API REST (FastAPI + OpenAI)
└── frontend/   ← App mobile (React Native) [em desenvolvimento]
```

---

## 🔧 Backend

### Visão Geral

API REST construída com **FastAPI** que usa a **OpenAI** para gerar quizzes dinâmicos de tecnologia. Roda localmente e é exposta publicamente via **ngrok** para integração com o app mobile.

### Stack

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12+ | Linguagem base |
| FastAPI | 0.110.0 | Framework web |
| Uvicorn | 0.28.0 | Servidor ASGI |
| Pydantic | 2.6.1 | Validação de dados |
| OpenAI SDK | 1.13.3 | Integração com GPT |
| python-dotenv | 1.0.1 | Variáveis de ambiente |
| ngrok | — | Exposição pública da API |

### Modelo de IA

`gpt-4.1-mini` — rápido, econômico e preciso para geração de perguntas.

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Healthcheck |
| `GET` | `/generate_quiz` | Gera 12 perguntas de tecnologia |
| `POST` | `/help` | Retorna dica para uma pergunta |
| `POST` | `/score` | Calcula pontuação da partida |

### Regras de Pontuação

| Dificuldade | Pontos |
|---|---|
| Fácil | 10 |
| Média | 20 |
| Difícil | 30 |

- Distribuição: **4 fáceis + 4 médias + 4 difíceis = 12 perguntas**
- Pontuação máxima: **240 pts**
- A partida **para ao primeiro erro** e retorna a pontuação acumulada

### Como Rodar

```bash
# 1. Instalar dependências
cd backend
pip install -r requirements.txt

# 2. Configurar variável de ambiente
echo OPENAI_API_KEY=sk-proj-... > .env

# 3. Subir a API
python -m uvicorn app.main:app --reload

# 4. (Dev) Expor com ngrok OU (Produção) deploy no Render — ver DEPLOY.md
ngrok http 8000
```

Documentação interativa: `http://localhost:8000/docs`

### Deploy em produção

Passo a passo completo (Render + `EXPO_PUBLIC_API_URL` + EAS): **[DEPLOY.md](./DEPLOY.md)**

### Estrutura

```
backend/
├── app/
│   ├── main.py                  ← rotas HTTP
│   ├── models/
│   │   └── quiz_models.py       ← schemas Pydantic
│   └── services/
│       ├── openai_service.py    ← integração OpenAI
│       └── quiz_service.py      ← lógica de negócio
├── testes/
├── .env                         ← 🔒 não sobe pro git
├── requirements.txt
├── README.md                    ← documentação da API
└── ARCHITECTURE.md              ← arquitetura detalhada
```

---

## 📱 Frontend

App **Expo / React Native** em `frontend/`.

```bash
cd frontend
cp .env.example .env   # preencha EXPO_PUBLIC_API_URL após o deploy da API
npm install
npx expo start
```

Deploy do app (EAS): ver **[DEPLOY.md](./DEPLOY.md)**.

---

## 📄 Licença

Projeto acadêmico — uso educacional.
