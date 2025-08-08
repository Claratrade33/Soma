from flask import Blueprint

bp = Blueprint('estatisticas', __name__, url_prefix='/estatisticas')

from . import rotas
