"""Rotas para a aplicação de inteligência financeira."""

import os
from flask import render_template, request
from openai import OpenAI

from . import bp
from .utils import (
    calcular_comissao,
    calcular_macd,
    calcular_media_movel,
    calcular_performance,
    calcular_rsi,
    obter_dados_mercado,
)


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


@bp.route('/')
def analise():
    """Calcula indicadores e consulta o GPT para gerar uma análise."""

    ticker = request.args.get("ticker", "demo")
    periodo_rsi = request.args.get("rsi_periodo", 14, type=int)
    macd_curto = request.args.get("macd_curto", 12, type=int)
    macd_longo = request.args.get("macd_longo", 26, type=int)
    macd_sinal = request.args.get("macd_sinal", 9, type=int)
    mm_periodo = request.args.get("mm_periodo", 20, type=int)
    taxa = request.args.get("taxa", 0.001, type=float)

    valores = obter_dados_mercado(ticker)
    erro_dados = False
    if not valores:
        erro_dados = True
        valores = [
            100, 101, 102, 99, 98, 100, 102, 101, 103, 105,
            104, 106, 108, 107, 109, 111, 110, 112, 115, 113,
            114, 116, 118, 117, 119, 121, 120, 122, 124, 123,
            125, 127, 126, 128, 130, 129, 131, 133, 132, 134,
        ]

    rsi = calcular_rsi(valores, periodo_rsi)
    macd, sinal = calcular_macd(valores, macd_curto, macd_longo, macd_sinal)
    media_movel = calcular_media_movel(valores, mm_periodo)
    performance = calcular_performance(valores)
    comissao = calcular_comissao(performance, taxa)
    performance_liquida = performance - comissao

    analise_texto = "OPENAI_API_KEY não configurada"
    if client is not None:
        prompt = (
            "Você é uma IA analista financeira. Considere os indicadores a seguir\n"
            f"RSI: {rsi:.2f}\n"
            f"MACD: {macd:.2f}\n"
            f"Sinal: {sinal:.2f}\n"
            f"Média Móvel: {media_movel:.2f}\n"
            f"Performance: {performance_liquida:.2f}% após comissões\n"
            "Forneça uma breve análise combinando estes indicadores."
        )
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=200,
            )
            analise_texto = resp.choices[0].message.content.strip()
        except Exception as e:
            analise_texto = f"Erro ao consultar GPT: {e}"

    contexto = {
        "rsi": rsi,
        "macd": macd,
        "sinal": sinal,
        "media_movel": media_movel,
        "valores": valores,
        "performance": performance,
        "comissao": comissao,
        "performance_liquida": performance_liquida,
        "analise": analise_texto,
        "erro_dados": erro_dados,
        "ticker": ticker,
        "rsi_periodo": periodo_rsi,
        "macd_curto": macd_curto,
        "macd_longo": macd_longo,
        "macd_sinal": macd_sinal,
        "mm_periodo": mm_periodo,
        "taxa": taxa,
    }
    return render_template("inteligencia_financeira/analise.html", **contexto)
