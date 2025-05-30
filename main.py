from flask import Flask, jsonify
import teste  # importa o script de teste

app = Flask(__name__)

@app.route("/executar", methods=["GET"])
def executar_teste():
    resultado = teste.executar()
    return jsonify({"mensagem": resultado})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
