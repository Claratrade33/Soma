from flask import Blueprint, render_template, request

bp_painel_operacao = Blueprint('painel_operacao', __name__, url_prefix='/painel')

@bp_painel_operacao.route('/dashboard')
def dashboard():
    contexto = {
        "alerta_dashboard": "Bem-vinda ao dashboard de operações.",
        "saldo": 1024.50,
        "lucro_24h": 25.35,
        "abertas": 3,
        "inicio": request.args.get("inicio", ""),
        "fim": request.args.get("fim", ""),
        "destaques": [
            {"par": "BTC/USDT", "preco": "67450", "direcao": "COMPRA", "status": "aguardando", "extra": "RSI 1h = 40"},
            {"par": "ETH/USDT", "preco": "3520", "direcao": "VENDA", "status": "aberta", "extra": "Alvo 1 em 1.5%"},
            {"par": "BNB/USDT", "preco": "590", "direcao": "COMPRA", "status": "encerrada", "extra": "P/L +1.9%"},
        ],
        "ops_tabela": [
            {"par": "BTC/USDT", "tipo": "COMPRA", "preco": "67450", "qtd": 0.01, "status": "aberta", "atualizado_em": "agora"},
            {"par": "ETH/USDT", "tipo": "VENDA", "preco": "3520", "qtd": 0.5, "status": "encerrada", "atualizado_em": "há 1h"},
            {"par": "BNB/USDT", "tipo": "COMPRA", "preco": "590", "qtd": 2, "status": "aguardando", "atualizado_em": "há 5min"},
        ],
        "pagina": int(request.args.get("page", 1)),
        "total_paginas": 2
    }
    return render_template("painel_operacao/dashboard.html", **contexto)