from flask_sqlalchemy import SQLAlchemy

# Instância global do banco de dados

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)


class BinanceKey(db.Model):
    __tablename__ = 'binance_key'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    api_secret = db.Column(db.String(255), nullable=False)
    testnet = db.Column(db.Boolean, default=True)
    openai_key = db.Column(db.String(255))

    usuario = db.relationship('Usuario', backref=db.backref('binance_key', uselist=False))
