"""Helpers for Clarinha's interaction with the OpenAI API."""

import os
from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def interpretar_pergunta(pergunta_usuario: str) -> str:
    """Consulta o modelo da OpenAI para interpretar a pergunta."""
    if client is None:
        return "OPENAI_API_KEY não configurada"

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


