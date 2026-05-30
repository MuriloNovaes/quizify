import json
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

# backend/.env (funciona mesmo se o cwd não for a pasta backend)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path, override=True)

class OpenAIService:
    def __init__(self):
        # A chave de API será lida automaticamente da variável de ambiente OPENAI_API_KEY
        self.client = OpenAI()

    def generate_chat_completion(self, system_prompt: str, user_prompt: str, response_format: str = "json_object"):
        """
        Método genérico para gerar respostas da OpenAI.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": response_format},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Erro na chamada da OpenAI: {str(e)}")
