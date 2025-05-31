from flask import Flask, jsonify, request
import subprocess
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Token de autenticação
AUTH_TOKEN = "wKu1b87dqXeuX9YK3Lr5u6KdbraMXlaB"

# Carrega .env
load_dotenv()

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

@app.route("/executar-login", methods=["POST"])
def executar_login():
    erro = require_token()
    if erro: return erro

    try:
        resultado = subprocess.run(["python", "login_playon.py"], capture_output=True, text=True, timeout=120)
        return jsonify({
            "status": "ok",
            "saida": resultado.stdout,
            "erro": resultado.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"erro": "Timeout na execução do script login_playon.py"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro ao executar script: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
