import openai

class ClarinhaIA:
    def gerar_sugestao(self, modo='real', chave=None):
        try:
            openai.api_key = chave
            prompt = "Com base no mercado BTC/USDT agora, me diga: entrada, alvo, stop e confiança (em JSON)"
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            conteudo = resposta.choices[0].message.content
            return conteudo
        except Exception:
            return '{"entrada": null, "alvo": null, "stop": null, "confianca": 0}'