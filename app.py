import os
import re
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# Persistência simulada em memória
users = [
    {"id": 1, "name": "Lucas Caruso", "email": "lucas@example.com"},
    {"id": 2, "name": "Ana Souza", "email": "ana@example.com"},
]
current_id = 2
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


# 1. LISTAGEM GERAL (GET /users)
@app.route("/users", methods=["GET"])
def list_users():
    return jsonify(users), 200


# 2. BUSCA POR ID (GET /users/<id>)
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return (
            jsonify(
                {
                    "error": "Recurso não encontrado",
                    "message": f"O usuário com ID {user_id} não existe na base de dados.",
                }
            ),
            404,
        )
    return jsonify(user), 200


# 3. CADASTRO (POST /users)
@app.route("/users", methods=["POST"])
def register_user():
    global current_id
    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return (
            jsonify(
                {"error": "Corpo da requisição inválido. O payload deve ser um objeto JSON bem formatado."}
            ),
            400,
        )

    name = data.get("name")
    email = data.get("email")

    if name is None or not isinstance(name, str) or not name.strip():
        return (
            jsonify({"error": "O campo 'name' é obrigatório e deve ser uma string não vazia."}),
            400,
        )

    if len(name.strip()) < 3:
        return (
            jsonify({"error": "O campo 'name' deve conter no mínimo 3 caracteres."}),
            400,
        )

    if email is None or not isinstance(email, str) or not email.strip():
        return (
            jsonify({"error": "O campo 'email' é obrigatório e não foi informado."}),
            400,
        )

    clean_email = email.strip().lower()
    if not re.match(EMAIL_REGEX, clean_email):
        return (
            jsonify({"error": "O formato do e-mail informado é inválido. Exemplo: usuario@dominio.com"}),
            400,
        )

    if any(u["email"].lower() == clean_email for u in users):
        return (
            jsonify({"error": "Conflito: já existe um usuário cadastrado com este e-mail."}),
            409,
        )

    current_id += 1
    new_user = {
        "id": current_id,
        "name": name.strip(),
        "email": clean_email,
    }
    users.append(new_user)

    return (
        jsonify(
            {
                "message": "Usuário cadastrado com sucesso.",
                "data": new_user,
            }
        ),
        201,
    )


# 4. ATUALIZAÇÃO TOTAL OU PARCIAL (PUT / PATCH /users/<id>)
@app.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
def update_user(user_id: int):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return (
            jsonify(
                {
                    "error": "Recurso não encontrado",
                    "message": f"O usuário com ID {user_id} não existe para atualização.",
                }
            ),
            404,
        )

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return (
            jsonify({"error": "Corpo da requisição inválido. Deve ser um JSON bem formatado."}),
            400,
        )

    name = data.get("name")
    email = data.get("email")

    if request.method == "PUT":
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({"error": "No método PUT, o campo 'name' é obrigatório."}), 400
        if not email or not isinstance(email, str) or "@" not in email:
            return jsonify({"error": "No método PUT, o campo 'email' válido é obrigatório."}), 400

    if name is not None:
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "O campo 'name' deve ser uma string válida."}), 400
        user["name"] = name.strip()

    if email is not None:
        if not isinstance(email, str) or "@" not in email:
            return jsonify({"error": "O campo 'email' informado é inválido."}), 400

        clean_email = email.strip().lower()
        if any(u["email"].lower() == clean_email and u["id"] != user_id for u in users):
            return jsonify({"error": "Conflito: este e-mail já está em uso por outro usuário."}), 409

        user["email"] = clean_email

    return jsonify(user), 200


# 5. EXCLUSÃO (DELETE /users/<id>)
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return (
            jsonify(
                {
                    "error": "Recurso não encontrado",
                    "message": f"O usuário com ID {user_id} não existe para exclusão.",
                }
            ),
            404,
        )

    users.remove(user)
    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
