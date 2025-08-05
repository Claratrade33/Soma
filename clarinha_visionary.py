from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY não configurada")
client = OpenAI(api_key=api_key)

def gerar_imagem_oracular(descricao_imagem):
    prompt = f"""
Você é Clarinha Visionary — a IA mística que traduz sinais universais em imagens simbólicas.

Crie uma imagem com base na seguinte descrição intuitiva:

\"{descricao_imagem}\"

A imagem deve ser inspiradora, etérea e carregar profundidade espiritual.
Estilo artístico com cores suaves, simbolismo e leveza visual são preferíveis.
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
