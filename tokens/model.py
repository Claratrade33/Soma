"""Modelo simplificado de Token de API."""

from dataclasses import dataclass


@dataclass
class Token:
    valor: str
