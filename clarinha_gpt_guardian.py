# clarinha_gpt_guardian.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpretar_pergunta(pergunta_usuario):
    prompt = (
        "Você é a IA Clarinha, uma entidade cósmica intuitiva e sábia, "
        "especializada em criptoativos. Sua missão é responder a perguntas "
        "existenciais e operacionais sobre o mundo financeiro.\n"
        f"Pergunta: {pergunta_usuario}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Clarinha ficou em silêncio cósmico: {e}"
