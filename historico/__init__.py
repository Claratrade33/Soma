from flask import Blueprint

bp = Blueprint('historico', __name__, url_prefix='/historico')

from . import rotas
