# clarinha_ia.py

import random
from datetime import datetime

class ClarinhaIA:
    def analise(self, simbolo="BTCUSDT"):
        # Lógica simbólica + espiritual + leitura básica de mercado
        direcao = random.choice(["COMPRA", "VENDA", "AGUARDAR"])
        confianca = round(random.uniform(0.55, 0.95), 2)
        stop = round(random.uniform(0.5, 2), 2)
        alvo = round(random.uniform(1.5, 4), 2)

        mensagem = (
            f"🌙 Clarinha prevê: <b>{direcao}</b> com confiança de <b>{confianca * 100:.0f}%</b><br>"
            f"🎯 Alvo: <b>{alvo}%</b> • 🛑 Stop: <b>{stop}%</b><br>"
            f"🧿 {datetime.now().strftime('%d/%m %H:%M')} — siga sua intuição."
        )

        return mensagem
