from flask import Blueprint

bp = Blueprint('claranews', __name__, url_prefix='/claranews')

from . import rotas
