from flask import Blueprint

bp = Blueprint('tokens', __name__, url_prefix='/tokens')

from . import rotas
