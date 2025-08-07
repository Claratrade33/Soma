"""Funções utilitárias para conectores de APIs externas."""


def testar_conexao(api_key: str, api_secret: str) -> bool:
    """Simula teste de conexão com o serviço externo."""
    return bool(api_key and api_secret)
