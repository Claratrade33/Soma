from flask import Blueprint

bp = Blueprint('monitoramento', __name__, url_prefix='/monitoramento')

from . import rotas
