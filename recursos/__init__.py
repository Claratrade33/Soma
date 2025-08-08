from flask import Blueprint

bp = Blueprint('recursos', __name__, url_prefix='/recursos')

from . import rotas
