"""Funções auxiliares para análise financeira."""

from __future__ import annotations

import functools
from typing import Iterable

import requests


def calcular_indicador_exemplo(valores: Iterable[float]) -> float:
    """Retorna a média simples dos valores fornecidos."""
    valores = list(valores)
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


@functools.lru_cache(maxsize=32)
def obter_dados_mercado(ticker: str) -> list[float]:
    """Obtém preços de mercado para ``ticker``.

    A função faz uma requisição HTTP simples e implementa ``lru_cache`` para
    evitar chamadas repetidas. Qualquer exceção é capturada e uma lista vazia
    é retornada, permitindo que a aplicação continue funcionando mesmo sem
    conexão com a API externa.
    """

    url = f"https://example.com/market/{ticker}"
    try:
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json().get("precos", [])
        if not isinstance(dados, list):
            return []
        return [float(v) for v in dados]
    except Exception:
        return []


def calcular_rsi(valores: list[float], periodo: int = 14) -> float:
    """Calcula o Índice de Força Relativa (RSI).

    O RSI é um oscilador que mede a velocidade e a mudança dos movimentos de preço.
    Esta implementação utiliza a média simples dos ganhos e perdas dos últimos
    ``periodo`` preços informados.

    Args:
        valores: Lista de preços de fechamento.
        periodo: Janela de cálculo do RSI. Padrão de 14 períodos.

    Returns:
        Valor do RSI entre 0 e 100. Retorna 0 caso não haja dados suficientes.
    """

    if len(valores) < periodo + 1:
        return 0.0

    ganhos = 0.0
    perdas = 0.0
    for i in range(-periodo, 0):
        delta = valores[i] - valores[i - 1]
        if delta > 0:
            ganhos += delta
        else:
            perdas += -delta

    if periodo == 0:
        return 0.0

    media_ganho = ganhos / periodo
    media_perda = perdas / periodo

    if media_perda == 0:
        return 100.0

    rs = media_ganho / media_perda
    return 100 - (100 / (1 + rs))


def calcular_macd(
    valores: list[float], curto: int = 12, longo: int = 26, sinal: int = 9
) -> tuple[float, float]:
    """Calcula o MACD (Moving Average Convergence Divergence).

    Retorna a linha MACD e a linha de sinal usando médias móveis exponenciais
    simples. Caso a lista de valores não seja suficiente, devolve (0.0, 0.0).

    Args:
        valores: Lista de preços de fechamento.
        curto: Período da média móvel exponencial curta (EMA rápida).
        longo: Período da média móvel exponencial longa (EMA lenta).
        sinal: Período da média móvel da linha MACD.

    Returns:
        Tupla ``(macd, sinal)`` com os valores calculados.
    """

    if not valores:
        return 0.0, 0.0

    def ema_series(dados: list[float], periodo: int) -> list[float]:
        """Retorna a série EMA para os dados informados."""
        k = 2 / (periodo + 1)
        ema_valor = dados[0]
        serie = [ema_valor]
        for preco in dados[1:]:
            ema_valor = preco * k + ema_valor * (1 - k)
            serie.append(ema_valor)
        return serie

    ema_curta = ema_series(valores, curto)
    ema_longa = ema_series(valores, longo)

    # Ajusta as séries para terem o mesmo tamanho
    tamanho = min(len(ema_curta), len(ema_longa))
    macd_series = [ema_curta[i] - ema_longa[i] for i in range(tamanho)]

    sinal_series = ema_series(macd_series, sinal)

    return macd_series[-1], sinal_series[-1]


def calcular_media_movel(valores: Iterable[float], periodo: int = 20) -> float:
    """Calcula a média móvel simples para ``periodo``."""
    valores = list(valores)
    if len(valores) < periodo or periodo <= 0:
        return 0.0
    return sum(valores[-periodo:]) / periodo


def calcular_performance(valores: Iterable[float]) -> float:
    """Retorna a variação percentual entre o primeiro e o último valor."""
    valores = list(valores)
    if len(valores) < 2:
        return 0.0
    inicial, final = valores[0], valores[-1]
    if inicial == 0:
        return 0.0
    return (final - inicial) / inicial * 100


def calcular_comissao(valor: float, taxa: float = 0.001) -> float:
    """Calcula a comissão sobre ``valor`` aplicando ``taxa``."""
    return valor * taxa
