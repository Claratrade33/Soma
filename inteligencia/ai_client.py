import os
from typing import List, Dict

import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "Você é a Clara, assistente de trading da ClaraVerse. "
    "Responda de forma prática, objetiva e com foco em risco/retorno."
)

def chat_responder(mensagem: str, contexto: List[Dict] | None = None, modelo: str = "gpt-4o-mini") -> str:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if contexto:
        msgs.extend(contexto)
    msgs.append({"role": "user", "content": mensagem})

    try:
        resp = openai.ChatCompletion.create(model=modelo, messages=msgs)
        return resp.choices[0].message.content
    except Exception as e:
        return f"[IA indisponível] {e}"