from flask import Blueprint

bp = Blueprint('resgates', __name__, url_prefix='/resgates')

from . import rotas
