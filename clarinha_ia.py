import random

class ClarinhaIA:
    def analise(self):
        sinais = ['ENTRADA COMPRADA', 'ENTRADA VENDIDA', 'AGUARDAR', 'STOP CURTO', 'ALVO LONGO']
        confianca = round(random.uniform(0.6, 0.99), 2)
        simbolo = "BTCUSDT"
        direcao = random.choice(sinais)
        retorno = {
            'simbolo': simbolo,
            'entrada': round(random.uniform(20000, 70000), 2),
            'alvo': round(random.uniform(entrada := random.uniform(20000, 70000), entrada + 1000), 2),
            'stop': round(entrada - 300, 2),
            'direcao': direcao,
            'confianca': confianca,
            'mensagem': f"A IA Clarinha sugere: {direcao} com confiança de {confianca * 100:.0f}%"
        }
        return retorno
