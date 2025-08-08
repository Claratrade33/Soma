from flask import Blueprint

bp = Blueprint('sinais', __name__, url_prefix='/sinais')

from . import rotas
