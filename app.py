from flask import Flask, render_template, request
from clarinha_core import clarinha_responder

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        pergunta = request.form["pergunta"]
        simbolo = request.form.get("simbolo", "BTCUSDT")
        gerar_imagem = "imagem" in request.form

        resultado = clarinha_responder(pergunta, simbolo, gerar_imagem)

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
