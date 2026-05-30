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
EXPO_PUBLIC_API_URL=https://quizify-api-339f.onrender.com
```

Reinicie o Expo após alterar o `.env`:

```bash
cd frontend
npm install
npx expo start
```

O app usa `lib/api-config.ts` — com a variável definida, entra em **modo conectado** e chama a API em HTTPS.

---

## 4. Web estática (cenário 3 — Vercel ou similar)

### Gerar o build (já feito localmente)

```bash
cd frontend
npx expo export --platform web
```

Saída: pasta `frontend/dist/` (não commitar — está no `.gitignore`).

A URL da API é embutida no build a partir de `EXPO_PUBLIC_API_URL` no `.env` no momento do export.

### Publicar na Vercel

O app fica em `frontend/` (monorepo). Existe **só** `frontend/vercel.json`.

#### Opção A — GitHub conectado (corrige o 404)

No painel da Vercel → projeto → **Settings → Build & Deployment**:

| Campo | Valor |
|--------|--------|
| **Root Directory** | `frontend`  ← **causa mais comum do 404** |
| Framework Preset | Other |
| Build Command | `npx expo export --platform web` |
| Output Directory | `dist` |
| Install Command | `npm install` |

**Settings → Environment Variables:**

- `EXPO_PUBLIC_API_URL` = `https://quizify-api-339f.onrender.com`

Depois: **Deployments → Redeploy**.

> Com **Root Directory = `frontend`**, a Vercel lê `frontend/vercel.json` e serve `frontend/dist/index.html`. Se ficar vazio/`.`, dá `404: NOT_FOUND`.

#### Opção B — Deploy direto da pasta `dist` (CLI, sem build na Vercel)

Mais à prova de erro: publica o `dist` já gerado.

```bash
cd frontend
npx expo export --platform web   # gera dist/ com a API embutida
cd dist
npx vercel login                 # autentica pelo navegador
npx vercel --prod                # publica esta pasta como site
```

Como o `dist` tem `index.html` na raiz, a Vercel serve direto — sem build, sem monorepo.

URL final: algo como `https://quizify-app.vercel.app`.

### Deploy rápido só da pasta `dist` (sem rebuild na Vercel)

```bash
cd frontend/dist
npx vercel --prod
```

Use isso se o `dist` local já foi gerado com o `.env` correto.

### Testar localmente o build de produção

```bash
cd frontend
npx serve dist
```

Abra a URL que o `serve` mostrar (ex.: http://localhost:3000).

---

## 5. Build mobile (EAS)

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

## 6. Checklist pós-deploy

URL atual da API: **https://quizify-api-339f.onrender.com**

- [x] `GET /` responde 200 na URL do Render.
- [ ] `OPENAI_API_KEY` configurada no painel Render → Environment (obrigatório para gerar quiz).
- [x] `frontend/.env` com `EXPO_PUBLIC_API_URL=https://quizify-api-339f.onrender.com`
- [x] `frontend/eas.json` atualizado com a mesma URL (builds EAS).
- [ ] App reiniciado (`npx expo start -c`).
- [ ] Teste `POST /quiz/start` pelo app ou em `/docs`.
- [ ] Web: `npx expo export --platform web` e deploy de `frontend/dist` (Vercel).
- [ ] Na Vercel: `EXPO_PUBLIC_API_URL` nas variáveis de build (se o deploy rebuildar no servidor).

---

## 7. Problemas comuns

| Sintoma | Solução |
|---------|---------|
| App em modo offline | `EXPO_PUBLIC_API_URL` vazia ou `.env` não carregado — reinicie o Expo. |
| Timeout na primeira chamada | Plano free do Render “acordando”; tente de novo. |
| 500 ao gerar quiz | Verifique `OPENAI_API_KEY` nos Environment do Render. |
| CORS | API já usa `allow_origins=["*"]` — suficiente para mobile e Expo Web. |
| Vercel `404: NOT_FOUND` | Root Directory / `outputDirectory` incorretos; use `vercel.json` da raiz ou `frontend` + redeploy. |
| Rota do app 404 no Vercel | Rode `npx expo export --platform web` de novo; `public/vercel.json` copia `cleanUrls` para `dist`. |

---

## 8. Substituir ngrok

Antes (dev):

```bash
python -m uvicorn app.main:app --reload
ngrok http 8000
```

Depois (produção / testes com celular):

- API fixa: `https://quizify-api-339f.onrender.com`
- App: `EXPO_PUBLIC_API_URL` apontando para essa URL.
