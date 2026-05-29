import uuid
from app.services.openai_service import OpenAIService
from app.models.quiz_models import (
    Difficulty,
    GeneratedQuestion,
    QuizResponse,
    HelpResponse,
    POINTS_BY_DIFFICULTY,
    FrontendQuestion,
    StartQuizResponse,
    HintResponse,
    LEVEL_TO_DIFFICULTY,
    DIFFICULTY_TO_LEVEL,
    VALID_THEME_IDS,
)

# Distribuição padrão da partida: 4 fáceis + 4 médias + 4 difíceis = 12 questões.
DEFAULT_PATTERN = (
    ["easy"] * 4 + ["medium"] * 4 + ["hard"] * 4
)

# Aceita variações de acento/caixa que a IA possa devolver para o nível.
_LEVEL_ALIASES = {
    "easy": "easy", "facil": "easy", "fácil": "easy", "fáceis": "easy", "faceis": "easy",
    "medium": "medium", "media": "medium", "média": "medium", "médias": "medium", "medias": "medium",
    "hard": "hard", "dificil": "hard", "difícil": "hard", "difíceis": "hard", "dificeis": "hard",
}


def _normalize_level(raw: str) -> str:
    return _LEVEL_ALIASES.get(str(raw).strip().lower(), "easy")


class QuizService:
    def __init__(self):
        self.openai_service = OpenAIService()
        # Cache em memória das questões geradas (id -> dados) para servir dicas (L-01).
        self._question_cache: dict[str, dict] = {}

    def generate_quiz(self, theme: str = "Tecnologia") -> QuizResponse:
        system_prompt = (
            f"Você é um gerador de quiz especializado em {theme}. "
            "Crie perguntas variadas cobrindo: linguagens de programação, frameworks, IDEs, "
            "estruturas de dados e algoritmos, banco de dados, backend, frontend e dados."
        )

        user_prompt = f"""
        Gere um quiz de 12 perguntas sobre '{theme}' distribuídas assim:
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
        {{
            "questions": [
                {{
                    "question": "Texto da pergunta",
                    "options": [
                        {{"text": "Opção 1", "is_correct": false}},
                        {{"text": "Opção 2", "is_correct": true}},
                        {{"text": "Opção 3", "is_correct": false}},
                        {{"text": "Opção 4", "is_correct": false}}
                    ],
                    "difficulty": "fácil",
                    "explanation": "Explicação breve"
                }}
            ]
        }}
        """

        data = self.openai_service.generate_chat_completion(system_prompt, user_prompt)
        questions_data = data.get("questions", [])

        questions = []
        for q in questions_data:
            difficulty = q.get("difficulty", "fácil")
            diff_enum = Difficulty(difficulty)
            questions.append(GeneratedQuestion(
                **q,
                points=POINTS_BY_DIFFICULTY.get(diff_enum, 10)
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

    # ----------------------------------------------------------------------
    # Endpoints consumidos diretamente pelo app (formato do frontend)
    # ----------------------------------------------------------------------

    def start_quiz(self, pattern: list[str] | None = None, theme: str = "Tecnologia") -> StartQuizResponse:
        """
        Gera 12 questões (4 fáceis, 4 médias, 4 difíceis) via OpenAI e devolve no
        formato esperado por `quiz-api.startQuiz`, já ordenadas conforme `pattern`.
        As questões são cacheadas em memória para servir dicas em `/quiz/hint`.
        """
        pattern = list(pattern) if pattern else list(DEFAULT_PATTERN)

        system_prompt = (
            f"Você é um gerador de quiz especializado em {theme}. "
            "Crie perguntas variadas e de alta qualidade cobrindo: linguagens de "
            "programação, frameworks, IDEs, estruturas de dados e algoritmos, banco "
            "de dados, backend, frontend, redes, autenticação e dados."
        )

        user_prompt = """
        Gere um quiz de EXATAMENTE 12 perguntas distribuídas assim:
        - 4 perguntas de nível 'easy'
        - 4 perguntas de nível 'medium'
        - 4 perguntas de nível 'hard'

        Para cada pergunta forneça:
        - "prompt": o enunciado da pergunta
        - "options": lista com EXATAMENTE 4 alternativas (apenas strings)
        - "correct_index": índice (0 a 3) da alternativa correta
        - "level": 'easy', 'medium' ou 'hard'
        - "theme": um destes ids exatos -> "languages", "logic", "data-structures",
          "networks", "databases", "auth-tokens", "ai"
        - "explanation": explicação curta da resposta correta
        - "hint": uma dica curta (máx. 20 palavras) que ajude a raciocinar SEM revelar a alternativa correta

        Responda em português brasileiro. Retorne JSON com a chave 'questions':
        {
            "questions": [
                {
                    "prompt": "Texto da pergunta",
                    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
                    "correct_index": 1,
                    "level": "easy",
                    "theme": "languages",
                    "explanation": "Explicação breve",
                    "hint": "Dica sutil"
                }
            ]
        }
        """

        data = self.openai_service.generate_chat_completion(system_prompt, user_prompt)
        raw_questions = data.get("questions", []) or []

        # Agrupa por nível para conseguir respeitar o pattern enviado pelo app.
        buckets: dict[str, list[dict]] = {"easy": [], "medium": [], "hard": []}
        for q in raw_questions:
            level = _normalize_level(q.get("level", "easy"))
            buckets[level].append(q)

        quiz_id = str(uuid.uuid4())
        attempt_id = f"att-{quiz_id[:8]}"
        questions: list[FrontendQuestion] = []

        def _build(raw: dict, level: str, position: int) -> FrontendQuestion | None:
            options = raw.get("options")
            if not isinstance(options, list) or len(options) < 4:
                return None
            options = [str(o) for o in options[:4]]

            correct_index = raw.get("correct_index", raw.get("correctIndex", 0))
            try:
                correct_index = int(correct_index)
            except (TypeError, ValueError):
                correct_index = 0
            if correct_index < 0 or correct_index > 3:
                correct_index = 0

            theme_id = str(raw.get("theme", raw.get("themeId", "languages")))
            if theme_id not in VALID_THEME_IDS:
                theme_id = "languages"

            qid = f"{attempt_id}-q{position:02d}"
            fq = FrontendQuestion(
                id=qid,
                themeId=theme_id,
                level=level,
                prompt=str(raw.get("prompt", raw.get("question", ""))),
                options=options,
                correctIndex=correct_index,
                explanation=str(raw.get("explanation", "")),
                hint=str(raw.get("hint", "")),
            )
            # Guarda no cache (sem expor o índice correto na dica).
            self._question_cache[qid] = {
                "prompt": fq.prompt,
                "options": fq.options,
                "hint": fq.hint,
            }
            return fq

        cursors = {"easy": 0, "medium": 0, "hard": 0}
        leftovers: list[dict] = []

        for i, level in enumerate(pattern):
            level = _normalize_level(level)
            pool = buckets.get(level, [])
            built = None
            while cursors[level] < len(pool) and built is None:
                built = _build(pool[cursors[level]], level, i + 1)
                cursors[level] += 1
            if built is not None:
                questions.append(built)

        # Caso a IA não tenha entregue a distribuição exata, completa com o que sobrou.
        if len(questions) < len(pattern):
            for level in ("easy", "medium", "hard"):
                pool = buckets.get(level, [])
                while cursors[level] < len(pool):
                    leftovers.append((level, pool[cursors[level]]))
                    cursors[level] += 1
            li = 0
            while len(questions) < len(pattern) and li < len(leftovers):
                level, raw = leftovers[li]
                built = _build(raw, level, len(questions) + 1)
                if built is not None:
                    questions.append(built)
                li += 1

        return StartQuizResponse(attemptId=attempt_id, questions=questions)

    def get_hint(self, question_id: str) -> HintResponse:
        """
        Dica server-side (L-01). Usa a questão cacheada para pedir à OpenAI uma dica
        que não revele a resposta. Em falha, devolve a dica pré-gerada da questão.
        """
        cached = self._question_cache.get(question_id)
        if not cached:
            # Sem contexto da questão; o app cai no fallback local automaticamente.
            return HintResponse(hint="")

        fallback = cached.get("hint") or "Elimine as alternativas claramente erradas e foque no conceito central."

        try:
            system_prompt = "Você é um assistente de quiz de tecnologia, útil e educativo."
            options_str = "\n".join(
                f"{chr(65 + i)}) {opt}" for i, opt in enumerate(cached.get("options", []))
            )
            user_prompt = f"""
            O jogador está em dúvida nesta questão de um quiz de tecnologia:

            Enunciado: {cached.get('prompt', '')}
            Alternativas:
            {options_str}

            Dê UMA única dica curta (máx. 25 palavras) em português brasileiro que ajude
            o jogador a raciocinar, SEM revelar qual é a alternativa correta nem citar a letra.
            Responda em JSON com a chave 'hint'.
            """
            data = self.openai_service.generate_chat_completion(system_prompt, user_prompt)
            hint = str(data.get("hint", "")).strip()
            return HintResponse(hint=hint or fallback)
        except Exception:
            return HintResponse(hint=fallback)

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
