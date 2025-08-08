"""Funções auxiliares para análise financeira."""


def calcular_indicador_exemplo(valores: list[float]) -> float:
    """Retorna a média simples dos valores fornecidos."""
    if not valores:
        return 0.0
    return sum(valores) / len(valores)
