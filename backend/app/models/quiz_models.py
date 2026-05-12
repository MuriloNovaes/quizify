from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Melhoria: Uso de Enum garante que a dificuldade seja sempre um desses três valores
class Difficulty(str, Enum):
    FACIL = "fácil"
    MEDIA = "média"
    DIFICIL = "difícil"

POINTS_BY_DIFFICULTY = {
    Difficulty.FACIL: 10,
    Difficulty.MEDIA: 20,
    Difficulty.DIFICIL: 30,
}

class QuestionOption(BaseModel):
    text: str = Field(..., description="Texto da opção de resposta")
    is_correct: bool = Field(..., description="Indica se esta é a resposta correta")

class GeneratedQuestion(BaseModel):
    question: str = Field(..., description="O enunciado da pergunta")
    options: List[QuestionOption] = Field(..., min_items=4, max_items=4, description="Lista com exatamente 4 opções")
    difficulty: Difficulty = Field(..., description="Nível de dificuldade da pergunta")
    points: int = Field(..., description="Pontuação atribuída à pergunta")
    explanation: Optional[str] = Field(None, description="Explicação educativa sobre a resposta correta")

class QuizResponse(BaseModel):
    quiz_id: str = Field(..., description="Identificador único da partida")
    questions: List[GeneratedQuestion] = Field(..., description="Lista de perguntas geradas")
    total_possible_points: int = Field(..., description="Soma total de pontos possíveis na partida")

class HelpRequest(BaseModel):
    question: str = Field(..., description="A pergunta para a qual o usuário precisa de ajuda")
    options: List[str] = Field(..., description="As opções de resposta disponíveis")

class HelpResponse(BaseModel):
    hint: str = Field(..., description="Dica sutil que não revela a resposta")
    explanation: str = Field(..., description="Explicação educativa sobre o tema")

class ScoreRequest(BaseModel):
    answers: List[bool] = Field(..., description="Lista de booleanos indicando acertos/erros na ordem")
    points_per_question: List[int] = Field(..., description="Lista de pontos correspondente a cada pergunta")

class ScoreResponse(BaseModel):
    score: int = Field(..., description="Pontuação final acumulada")
    total_possible: int = Field(..., description="Pontuação máxima que poderia ser atingida")
    correct: int = Field(..., description="Quantidade de acertos")
    total: int = Field(..., description="Total de perguntas respondidas")
