# clarinha_gpt_guardian.py
import openai
import random
import time
import hashlib
import uuid

class ClarinhaGPTGuardian:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.human_delay_range = (0.7, 2.5)

    def _gerar_id_mistico(self):
        base = uuid.uuid4().hex + str(time.time())
        return hashlib.sha256(base.encode()).hexdigest()[:24]

    def _comportamento_humano(self):
        tempo = random.uniform(*self.human_delay_range)
        time.sleep(tempo)

    def consultar(self, mensagem, modelo="gpt-4", temperatura=0.4):
        self._comportamento_humano()
        try:
            resposta = openai.ChatCompletion.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": "Você é uma IA espiritual de proteção e estratégia financeira."},
                    {"role": "user", "content": mensagem}
                ],
                temperature=temperatura,
                user=self._gerar_id_mistico()
            )
            return resposta.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Clarinha não conseguiu acessar os céus da OpenAI: {e}"