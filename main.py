from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def home():
    return jsonify({"mensagem": "API está rodando!"})

@app.route("/teste", methods=["GET"])
def teste():
    return jsonify({"mensagem": "Estou funcionando!"})

@app.route("/ativaruser", methods=["GET"])
def ativar_usuario():
    usuario = request.args.get("usuario")
    if not usuario:
        return jsonify({"erro": "Parâmetro 'usuario' não fornecido"}), 400
    return jsonify({"mensagem": f"Usuário {usuario} ativado com sucesso!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
