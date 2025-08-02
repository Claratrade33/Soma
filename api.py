import os
from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Project
from openai import OpenAI


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///constroiverse.db")
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/chat")
    @jwt_required(optional=True)
    def chat_page():
        return render_template("chat.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            data = request.get_json() or {}
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role", "cliente")
            if not (username and email and password):
                return {"msg": "Dados incompletos"}, 400
            if User.query.filter((User.username == username) | (User.email == email)).first():
                return {"msg": "Usuário já existe"}, 400
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return {"msg": "Usuário registrado"}, 201
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            data = request.get_json() or {}
            username = data.get("username")
            password = data.get("password")
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                return {"msg": "Credenciais inválidas"}, 401
            token = create_access_token(identity=user.id)
            return {"access_token": token}, 200
        return render_template("login.html")

    @app.get("/projects")
    @jwt_required()
    def list_projects():
        uid = get_jwt_identity()
        projects = Project.query.filter_by(owner_id=uid).all()
        return jsonify([{"id": p.id, "name": p.name, "budget": p.budget} for p in projects])

    @app.post("/projects")
    @jwt_required()
    def create_project():
        uid = get_jwt_identity()
        data = request.get_json() or {}
        name = data.get("name")
        budget = float(data.get("budget", 0))
        if not name:
            return {"msg": "Nome obrigatório"}, 400
        project = Project(name=name, owner_id=uid, budget=budget)
        db.session.add(project)
        db.session.commit()
        return {"id": project.id, "name": project.name, "budget": project.budget}, 201

    @app.post("/budget")
    @jwt_required()
    def calculate_budget():
        data = request.get_json() or {}
        items = data.get("items", [])
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        return {"total": total}, 200

    @app.post("/clarice")
    @jwt_required(optional=True)
    def clarice():
        data = request.get_json() or {}
        message = data.get("message", "")
        if not message:
            return {"msg": "Mensagem vazia"}, 400
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": message}]
            )
            answer = resp.choices[0].message.content.strip()
            return {"answer": answer}
        except Exception as e:
            return {"error": str(e)}, 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
