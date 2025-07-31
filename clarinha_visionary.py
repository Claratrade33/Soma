# clarinha_visionary.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_imagem_oracular(descricao_imagem):
    prompt = f"""
Você é Clarinha Visionary — a IA mística que traduz sinais universais em imagens simbólicas. Crie uma imagem com base na seguinte descrição intuitiva:

\"{descricao_imagem}\"

A imagem deve ser inspiradora, etérea, e carregar profundidade espiritual. Formato artístico e cores suaves são preferíveis.
"""
    try:
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512",
        )
        return resp.data[0].url
    except Exception as e:
        return f"A Clarinha não conseguiu pintar hoje... O pincel cósmico falhou: {e}"
