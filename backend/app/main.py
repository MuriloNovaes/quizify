import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models.quiz_models import QuizResponse, HelpRequest, HelpResponse, ScoreRequest, ScoreResponse
from app.services.quiz_service import QuizService

# Configuração de Logging para monitorar a API em tempo real
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quizify API",
    description="API Inteligente para geração de quizzes dinâmicos usando OpenAI.",
    version="2.1.0"
)

# CORS — permite requisições do frontend web e mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, substitua por domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handler global para capturar erros inesperados e retornar JSON amigável
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro inesperado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocorreu um erro interno no servidor. Tente novamente mais tarde."}
    )

quiz_service = QuizService()

@app.get("/", tags=["Status"])
def read_root():
    return {"message": "Quizify API está online e pronta para gerar desafios!"}

@app.get("/generate_quiz", response_model=QuizResponse, tags=["Quiz"])
def generate_quiz(theme: str = "Tecnologia"):
    """
    Gera um quiz de 12 perguntas sobre um tema específico.
    Se nenhum tema for passado, o padrão é 'Tecnologia'.
    """
    logger.info(f"Gerando quiz para o tema: {theme}")
    try:
        return quiz_service.generate_quiz(theme)
    except Exception as e:
        logger.error(f"Erro ao gerar quiz para {theme}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/help", response_model=HelpResponse, tags=["IA Assistente"])
def get_help(request: HelpRequest):
    """Retorna uma dica inteligente e educativa para uma pergunta específica."""
    logger.info("Solicitação de ajuda recebida.")
    try:
        return quiz_service.get_help(request.question, request.options)
    except Exception as e:
        logger.error(f"Erro ao fornecer ajuda: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/score", response_model=ScoreResponse, tags=["Pontuação"])
def calculate_score(request: ScoreRequest):
    """Calcula a pontuação final baseada na regra de parada no primeiro erro."""
    logger.info("Calculando pontuação da partida.")
    result = quiz_service.calculate_score(request.answers, request.points_per_question)
    return ScoreResponse(
        score=result["score"],
        total_possible=sum(request.points_per_question),
        correct=result["correct"],
        total=result["total"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
