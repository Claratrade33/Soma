from flask import Blueprint, render_template, redirect
from operacoes_automatico.leitura_mercado import obter_dados_mercado
from operacoes_automatico.inteligencia import executar_estrategia

bp = Blueprint('operacoes_automatico', __name__)

@bp.route("/painel_automatico")
def painel_automatico():
    labels, dados = obter_dados_mercado("BTCUSDT")
    return render_template("operacoes/painel_automatico.html", labels=labels, dados=dados)

@bp.route("/operacoes_automatico/ativar", methods=["POST"])
def ativar():
    executar_estrategia()
    return redirect("/painel_automatico")
