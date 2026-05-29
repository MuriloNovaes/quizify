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


# --------------------------------------------------------------------------
# Contrato consumido diretamente pelo app (frontend Expo/React Native).
# Ver `frontend/docs/BACKEND-INTEGRATION.md` e `frontend/lib/quiz/quiz-api.ts`.
# --------------------------------------------------------------------------

# Níveis no formato esperado pelo app (inglês) e mapeamento de/para o Enum interno.
FrontendLevel = str  # 'easy' | 'medium' | 'hard'

DIFFICULTY_TO_LEVEL = {
    Difficulty.FACIL: "easy",
    Difficulty.MEDIA: "medium",
    Difficulty.DIFICIL: "hard",
}

LEVEL_TO_DIFFICULTY = {v: k for k, v in DIFFICULTY_TO_LEVEL.items()}

# Temas válidos no app (`frontend/lib/quiz/themes.ts`).
VALID_THEME_IDS = {
    "languages",
    "logic",
    "data-structures",
    "networks",
    "databases",
    "auth-tokens",
    "ai",
}


class FrontendQuestion(BaseModel):
    """Questão no formato exato consumido pelo app em `quiz-api.startQuiz`."""
    id: str = Field(..., description="Identificador único da questão")
    themeId: str = Field(..., description="Tema (um dos ids válidos do app)")
    level: FrontendLevel = Field(..., description="Nível: easy | medium | hard")
    prompt: str = Field(..., description="Enunciado da pergunta")
    options: List[str] = Field(..., min_items=4, max_items=4, description="4 alternativas (texto)")
    correctIndex: int = Field(..., ge=0, le=3, description="Índice (0..3) da alternativa correta")
    explanation: str = Field("", description="Explicação curta da resposta correta")
    hint: str = Field("", description="Dica que NÃO revela a resposta")


class StartQuizRequest(BaseModel):
    count: Optional[int] = Field(12, description="Quantidade de questões desejada")
    pattern: Optional[List[FrontendLevel]] = Field(
        None, description="Ordem de níveis esperada (easy/medium/hard)"
    )


class StartQuizResponse(BaseModel):
    attemptId: str = Field(..., description="Identificador da tentativa gerada")
    questions: List[FrontendQuestion] = Field(..., description="Questões na ordem do pattern")


class HintRequest(BaseModel):
    questionId: str = Field(..., description="Id da questão para a qual o usuário pediu dica")


class HintResponse(BaseModel):
    hint: str = Field(..., description="Dica curta (≤ 25 palavras) sem revelar a resposta")
