from clarinha_ia import solicitar_analise_json
from clarinha_gpt_guardian import interpretar_pergunta
from clarinha_visionary import gerar_imagem_oracular

def clarinha_responder(pergunta, simbolo="BTCUSDT", gerar_imagem=False):
    resposta_gpt = interpretar_pergunta(pergunta)
    analise_json = solicitar_analise_json(simbolo)
    imagem_url = gerar_imagem_oracular(pergunta) if gerar_imagem else "Imagem não solicitada."

    return {
        "resposta_guardian": resposta_gpt,
        "analise_operacional": analise_json,
        "imagem_oracular": imagem_url
    }
