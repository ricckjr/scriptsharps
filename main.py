from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/executar", methods=["GET"])
def executar():
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"erro": "CPF não informado"}), 400

    return jsonify({"resultado": f"Processado com sucesso para o CPF {cpf}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
