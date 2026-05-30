# Deploy Quizify (API + App)

Guia para publicar a **API FastAPI** no [Render](https://render.com) e conectar o **app Expo** sem ngrok.

---

## 1. Pré-requisitos

- Conta no [Render](https://render.com) e repositório no GitHub (`MuriloNovaes/quizify` ou fork).
- Chave OpenAI (`OPENAI_API_KEY`).
- Node.js instalado (para o app Expo).
- (Opcional) Conta [Expo](https://expo.dev) para builds com EAS.

---

## 2. Deploy da API no Render

### Opção A — Blueprint (recomendado)

1. No Render: **New** → **Blueprint**.
2. Conecte o repositório GitHub deste projeto.
3. O Render lê o arquivo `render.yaml` na raiz e cria o serviço `quizify-api`.
4. Quando pedir variáveis, defina **`OPENAI_API_KEY`** (marque como secret).
5. Aguarde o deploy. A URL ficará algo como:  
   `https://quizify-api.onrender.com`

### Opção B — Web Service manual

| Campo | Valor |
|--------|--------|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/` |

**Environment:**

| Key | Value |
|-----|--------|
| `OPENAI_API_KEY` | sua chave OpenAI |
| `PYTHON_VERSION` | `3.12.8` (opcional, recomendado) |

### Testar a API

Abra no navegador:

- `https://SUA-URL.onrender.com/` → deve retornar JSON de status.
- `https://SUA-URL.onrender.com/docs` → Swagger.

> No plano **free**, o serviço pode “dormir” após inatividade; a primeira requisição pode demorar ~30–60 s.

---

## 3. Conectar o app Expo à API

Na pasta `frontend/`:

```bash
cp .env.example .env
```

Edite `.env` e coloque a URL real (sem `/` no final):

```env
EXPO_PUBLIC_API_URL=https://quizify-api.onrender.com
```

Reinicie o Expo após alterar o `.env`:

```bash
cd frontend
npm install
npx expo start
```

O app usa `lib/api-config.ts` — com a variável definida, entra em **modo conectado** e chama a API em HTTPS.

---

## 4. Build de produção (EAS)

1. Instale a CLI: `npm install -g eas-cli`
2. Login: `eas login`
3. Na pasta `frontend/`, edite `eas.json` e troque `https://SUBSTITUA.onrender.com` pela URL do Render.
4. Configure o projeto: `eas build:configure`
5. Build Android (APK interno):  
   `eas build --platform android --profile preview`
6. Build produção:  
   `eas build --platform android --profile production`

As variáveis em `eas.json` → `env` → `EXPO_PUBLIC_API_URL` são embutidas no build.

---

## 5. Checklist pós-deploy

- [ ] `GET /` responde 200 na URL do Render.
- [ ] `OPENAI_API_KEY` configurada só no Render (nunca no Git).
- [ ] `frontend/.env` com `EXPO_PUBLIC_API_URL` em HTTPS.
- [ ] App reiniciado (`expo start -c` se cache antigo).
- [ ] Teste `POST /quiz/start` pelo app ou pelo Swagger.

---

## 6. Problemas comuns

| Sintoma | Solução |
|---------|---------|
| App em modo offline | `EXPO_PUBLIC_API_URL` vazia ou `.env` não carregado — reinicie o Expo. |
| Timeout na primeira chamada | Plano free do Render “acordando”; tente de novo. |
| 500 ao gerar quiz | Verifique `OPENAI_API_KEY` nos Environment do Render. |
| CORS | API já usa `allow_origins=["*"]` — suficiente para mobile e Expo Web. |

---

## 7. Substituir ngrok

Antes (dev):

```bash
uvicorn app.main:app --reload
ngrok http 8000
```

Depois (produção / testes com celular):

- API fixa: `https://quizify-api.onrender.com`
- App: `EXPO_PUBLIC_API_URL` apontando para essa URL.
