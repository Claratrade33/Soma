# clarinha_gpt_guardian.py

import openai

class ClarinhaGPTGuardian:
    def __init__(self, openai_key):
        self.api_key = openai_key
        openai.api_key = self.api_key

    def consultar(self, prompt):
        try:
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é Clarinha, uma IA espiritual que guia decisões financeiras com sabedoria e intuição."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300,
            )
            return resposta['choices'][0]['message']['content']
        except Exception as e:
            return f"Erro GPT: {e}"