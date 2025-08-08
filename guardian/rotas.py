from . import bp

@bp.route('/')
def index():
    return 'guardian placeholder'
