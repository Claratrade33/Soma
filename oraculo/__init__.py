from flask import Blueprint

bp = Blueprint('oraculo', __name__, url_prefix='/oraculo')

from . import rota_ia_sugestao
