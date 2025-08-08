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


def test_calcular_rsi_insuficiente():
    """RSI deve retornar 0 com dados insuficientes."""
    assert calcular_rsi([1, 2, 3], periodo=14) == 0.0


def test_calcular_macd_basic():
    valores = list(range(1, 60))
    macd, sinal = calcular_macd(valores)
    assert isinstance(macd, float)
    assert isinstance(sinal, float)


def test_calcular_macd_vazio():
    """MACD vazio retorna zeros."""
    macd, sinal = calcular_macd([])
    assert macd == 0.0 and sinal == 0.0


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


def test_analise_route_sem_api_key(monkeypatch):
    app = create_app()
    client = app.test_client()

    contexto = {}

    def fake_render(template, **ctx):
        contexto.update(ctx)
        return "ok"

    monkeypatch.setattr(rotas, "render_template", fake_render)
    monkeypatch.setattr(rotas, "obter_dados_mercado", lambda ticker: list(range(1, 60)))
    monkeypatch.setattr(rotas, "client", None)

    resp = client.get("/inteligencia_financeira/")
    assert resp.status_code == 200
    assert "OPENAI_API_KEY" in contexto["analise"]


def test_analise_route_erro_dados(monkeypatch):
    app = create_app()
    client = app.test_client()

    contexto = {}

    def fake_render(template, **ctx):
        contexto.update(ctx)
        return "ok"

    monkeypatch.setattr(rotas, "render_template", fake_render)
    monkeypatch.setattr(rotas, "obter_dados_mercado", lambda ticker: [])
    monkeypatch.setattr(rotas, "client", None)

    resp = client.get("/inteligencia_financeira/")
    assert resp.status_code == 200
    assert contexto["erro_dados"] is True
    assert len(contexto["valores"]) > 0
