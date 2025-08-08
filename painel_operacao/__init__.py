# painel_operacao/__init__.py
from flask import Blueprint

bp = Blueprint("painel_operacao", __name__, url_prefix="/painel")

# Importe as rotas após criar o blueprint
from . import rotas
