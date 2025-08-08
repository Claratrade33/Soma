from flask import Blueprint

bp = Blueprint('inteligencia_financeira', __name__, url_prefix='/inteligencia_financeira')

from . import rotas
