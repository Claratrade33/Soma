from flask import Blueprint

bp = Blueprint('comando', __name__, url_prefix='/comando')

from . import rotas
