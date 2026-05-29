import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv(override=True)

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
