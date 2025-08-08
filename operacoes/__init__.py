from flask import Blueprint

bp = Blueprint('operacoes', __name__, url_prefix='/operacoes')

from . import rotas
