from flask import Blueprint

bp = Blueprint('servicos', __name__, url_prefix='/servicos')

from . import rotas
