from pydantic import BaseModel
from typing import List, Optional

POINTS_BY_DIFFICULTY = {
    "fácil": 10,
    "média": 20,
    "difícil": 30,
}

class QuestionOption(BaseModel):
    text: str
    is_correct: bool

class GeneratedQuestion(BaseModel):
    question: str
    options: List[QuestionOption]
    difficulty: str  # 'fácil', 'média', 'difícil'
    points: int
    explanation: Optional[str] = None

class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[GeneratedQuestion]
    total_possible_points: int

class HelpRequest(BaseModel):
    question: str
    options: List[str]

class HelpResponse(BaseModel):
    hint: str
    explanation: str

class ScoreRequest(BaseModel):
    answers: List[bool]  # lista de acertos/erros na ordem das perguntas
    points_per_question: List[int]  # pontuação de cada pergunta

class ScoreResponse(BaseModel):
    score: int
    total_possible: int
    correct: int
    total: int
