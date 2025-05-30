from flask import Flask, jsonify, request

app = Flask(__name__)

# Token de autenticação
AUTH_TOKEN = "wKu1b87dqXeuX9YK3Lr5u6KdbraMXlaB"

# Middleware para validar token

def require_token():
    token = request.headers.get("Authorization")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"erro": "Token inválido ou ausente"}), 401

@app.route("/api", methods=["GET"])
def home():
    return jsonify({"mensagem": "API está rodando!"})

@app.route("/teste", methods=["GET"])
def teste():
    erro = require_token()
    if erro: return erro
    return jsonify({"mensagem": "Estou funcionando!"})

@app.route("/ativaruser", methods=["GET"])
def ativar_usuario():
    erro = require_token()
    if erro: return erro

    usuario = request.args.get("usuario")
    if not usuario:
        return jsonify({"erro": "Parâmetro 'usuario' é obrigatório"}), 400

    return jsonify({"mensagem": f"Usuário {usuario} ativado com sucesso!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
