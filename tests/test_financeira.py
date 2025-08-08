import pytest
from flask import Flask
import os

from inteligencia_financeira import bp as finance_bp
from inteligencia_financeira import rotas
from inteligencia_financeira.utils import (
    calcular_rsi,
    calcular_macd,
    calcular_media_movel,
    calcular_performance,
    calcular_comissao,
)


def create_app():
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    app = Flask(__name__, template_folder=template_dir)
    app.register_blueprint(finance_bp)
    return app


def test_calcular_rsi_basic():
    valores = list(range(1, 20))
    rsi = calcular_rsi(valores)
    assert 0 <= rsi <= 100



def test_calcular_macd_basic():
    valores = list(range(1, 60))
    macd, sinal = calcular_macd(valores)
    assert isinstance(macd, float)
    assert isinstance(sinal, float)



def test_utilidades_complementares():
    valores = [10, 12, 14, 16, 18, 20]
    assert calcular_media_movel(valores, 3) == pytest.approx(18)
    perf = calcular_performance(valores)
    assert perf > 0
    comissao = calcular_comissao(perf, 0.01)
    assert comissao == pytest.approx(perf * 0.01)


def test_analise_route(monkeypatch):
    app = create_app()
    client = app.test_client()

    # Garante dados determinísticos
    monkeypatch.setattr(rotas, "obter_dados_mercado", lambda ticker: list(range(1, 60)))
    monkeypatch.setattr(rotas, "render_template", lambda *a, **k: "ok")

    resp = client.get("/inteligencia_financeira/?rsi_periodo=14")
    assert resp.status_code == 200

