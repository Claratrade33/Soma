from flask import Blueprint

bp = Blueprint('painel_operacao', __name__, url_prefix='/painel_operacao')

from . import rotas
