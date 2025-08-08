from flask import Blueprint

bp = Blueprint('treinamentos', __name__, url_prefix='/treinamentos')

from . import rotas
