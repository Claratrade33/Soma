from flask import Blueprint, render_template, request

bp_operacoes_auto = Blueprint(
    "operacoes_automatico", __name__, url_prefix="/operacoes_automatico"
)

@bp_operacoes_auto.route("/painel")
def painel():
    contexto = {
        "status_msg": "Robô pronto para iniciar.",
        "robo_status": "parado",
        "par": "BTC/USDT",
        "timeframe": "15m",
        "estrategia": "RSI+MACD",
        "inicio": request.args.get("inicio", ""),
        "fim": request.args.get("fim", ""),
        "ops": [
            {"par": "BTC/USDT", "preco": "67450", "direcao": "COMPRA", "status": "aberta", "extra": "RSI 1h = 32"},
            {"par": "ETH/USDT", "preco": "3520", "direcao": "VENDA", "status": "aguardando", "extra": "MACD cruzou p/ baixo"},
        ],
        "pagina": int(request.args.get("page", 1)),
        "total_paginas": 3,
        "toast_titulo": "Aviso",
        "toast_msg": "Painel carregado com sucesso."
    }
    # GARANTE: o nome bate com a pasta/arquivo existente
    return render_template("operacoes/painel_automatico.html", **contexto)