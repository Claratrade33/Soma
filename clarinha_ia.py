import random
from datetime import datetime

class ClarinhaCosmo:
    def analisar(self, simbolo="BTCUSDT"):
        return {
            'sinal': random.choice(['BUY', 'SELL', 'HOLD']),
            'confianca': round(random.uniform(0.5, 0.99), 2),
            'risco': random.choice(['BAIXO', 'MÉDIO', 'ALTO']),
            'volume': random.randint(100000, 9000000),
            'timestamp': datetime.utcnow().isoformat()
        }

class ClarinhaOraculo:
    def prever(self, simbolo="BTCUSDT"):
        return {
            'tendencia': random.choice(['ALTA', 'BAIXA', 'NEUTRA']),
            'sentimento': random.choice(['OTIMISTA', 'PESSIMISTA', 'NEUTRO']),
            'pontuacao': round(random.uniform(-1, 1), 3),
            'timestamp': datetime.utcnow().isoformat()
        }

# IA Central que unifica Cosmo e Oráculo
class ClarinhaIA:
    def __init__(self):
        self.cosmo = ClarinhaCosmo()
        self.oraculo = ClarinhaOraculo()

    def gerar_sugestao(self, simbolo="BTCUSDT"):
        analise = self.cosmo.analisar(simbolo)
        previsao = self.oraculo.prever(simbolo)

        # Combinação das duas análises para sugerir ação final
        if analise['sinal'] == 'BUY' and previsao['tendencia'] == 'ALTA':
            acao = 'COMPRAR'
        elif analise['sinal'] == 'SELL' and previsao['tendencia'] == 'BAIXA':
            acao = 'VENDER'
        else:
            acao = 'AGUARDAR'

        return {
            'acao': acao,
            'sinal_cosmo': analise,
            'visao_oraculo': previsao
        }