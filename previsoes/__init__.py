from flask import Blueprint

bp = Blueprint('previsoes', __name__, url_prefix='/previsoes')

from . import rotas
