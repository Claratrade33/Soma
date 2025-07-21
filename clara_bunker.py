from app import app  # Importa a aplicação Flask do arquivo app.py

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Inicia a aplicação