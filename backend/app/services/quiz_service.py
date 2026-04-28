import uuid
from app.services.openai_service import OpenAIService
from app.models.quiz_models import GeneratedQuestion, QuizResponse, HelpResponse, POINTS_BY_DIFFICULTY

class QuizService:
    def __init__(self):
        self.openai_service = OpenAIService()

    def generate_quiz(self) -> QuizResponse:
        system_prompt = (
            "Você é um gerador de quiz especializado em tecnologia. "
            "Crie perguntas variadas cobrindo: linguagens de programação, frameworks, IDEs, "
            "estruturas de dados e algoritmos, banco de dados, backend, frontend e dados."
        )

        user_prompt = """
        Gere um quiz de 12 perguntas de tecnologia distribuídas assim:
        - 4 perguntas de dificuldade 'fácil'
        - 4 perguntas de dificuldade 'média'
        - 4 perguntas de dificuldade 'difícil'

        Varie os subtemas entre: linguagens de programação, frameworks, IDEs,
        estruturas de dados e algoritmos, banco de dados, backend, frontend e dados.

        Para cada pergunta forneça:
        - A pergunta
        - 4 opções de resposta (apenas uma correta)
        - O nível de dificuldade: 'fácil', 'média' ou 'difícil'
        - Uma breve explicação da resposta correta

        Retorne JSON com a chave 'questions':
        {
            "questions": [
                {
                    "question": "Texto da pergunta",
                    "options": [
                        {"text": "Opção 1", "is_correct": false},
                        {"text": "Opção 2", "is_correct": true},
                        {"text": "Opção 3", "is_correct": false},
                        {"text": "Opção 4", "is_correct": false}
                    ],
                    "difficulty": "fácil",
                    "explanation": "Explicação breve"
                }
            ]
        }
        """

        data = self.openai_service.generate_chat_completion(system_prompt, user_prompt)
        questions_data = data.get("questions", [])

        questions = []
        for q in questions_data:
            difficulty = q.get("difficulty", "fácil")
            questions.append(GeneratedQuestion(
                **q,
                points=POINTS_BY_DIFFICULTY.get(difficulty, 10)
            ))

        total_possible = sum(q.points for q in questions)

        return QuizResponse(
            quiz_id=str(uuid.uuid4()),
            questions=questions,
            total_possible_points=total_possible
        )

    def get_help(self, question: str, options: list[str]) -> HelpResponse:
        system_prompt = "Você é um assistente de quiz de tecnologia, útil e educativo."

        user_prompt = f"""
        O usuário está com dificuldade na seguinte pergunta:
        Pergunta: {question}
        Opções: {", ".join(options)}

        Forneça:
        1. Uma dica sutil que não revele a resposta diretamente.
        2. Uma explicação breve sobre o tema para ajudar o usuário a aprender.

        Responda em JSON com as chaves 'hint' e 'explanation'.
        """

        data = self.openai_service.generate_chat_completion(system_prompt, user_prompt)
        return HelpResponse(
            hint=data.get("hint", "Dica não disponível."),
            explanation=data.get("explanation", "Explicação não disponível.")
        )

    def calculate_score(self, answers: list[bool], points_per_question: list[int]) -> dict:
        score = 0
        for answered_correct, points in zip(answers, points_per_question):
            if answered_correct:
                score += points
            else:
                break  # para ao errar
        correct = sum(1 for a in answers if a)
        return {
            "score": score,
            "correct": correct,
            "total": len(answers)
        }
