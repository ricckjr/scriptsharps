from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def home():
    return jsonify({"mensagem": "API está rodando!"})

@app.route("/teste", methods=["GET"])
def teste():
    return jsonify({"mensagem": "Estou funcionando!"})

@app.route("/ativaruser", methods=["GET"])
def teste():
    usuario = request.args.get("usuario")
    return jsonify({"mensagem": "Estou funcionando!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
