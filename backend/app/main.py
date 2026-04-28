from fastapi import FastAPI, HTTPException
from app.models.quiz_models import QuizResponse, HelpRequest, HelpResponse, ScoreRequest, ScoreResponse
from app.services.quiz_service import QuizService

app = FastAPI(
    title="API Quiz de Tecnologia",
    description="Gera quizzes de tecnologia com pontuação usando OpenAI.",
    version="2.0.0"
)

quiz_service = QuizService()

@app.get("/")
def read_root():
    return {"message": "API Quiz de Tecnologia no ar!"}

@app.get("/generate_quiz", response_model=QuizResponse)
def generate_quiz():
    """Gera um quiz de 12 perguntas de tecnologia (4 fáceis, 4 médias, 4 difíceis)."""
    try:
        return quiz_service.generate_quiz()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/help", response_model=HelpResponse)
def get_help(request: HelpRequest):
    """Retorna uma dica para uma pergunta sem revelar a resposta."""
    try:
        return quiz_service.get_help(request.question, request.options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/score", response_model=ScoreResponse)
def calculate_score(request: ScoreRequest):
    """
    Calcula a pontuação da partida.
    Para ao primeiro erro e retorna a pontuação acumulada até ali.
    Se acertar todas, retorna a pontuação total.
    """
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
