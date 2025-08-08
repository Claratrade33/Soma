from flask import Blueprint

bp = Blueprint('registro', __name__, url_prefix='/registro')

from . import rotas
