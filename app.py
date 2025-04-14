from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "senha-super-secreta"  # Troque por uma mais segura se desejar

# Caminho do banco de dados
DB_PATH = "pedidos.db"

# Inicializa o banco de dados
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            telefone TEXT,
            carne INTEGER,
            frango INTEGER,
            brocolis INTEGER,
            total REAL,
            datahora TEXT
        )
    """)
    conn.commit()
    conn.close()

# Página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para salvar pedidos
@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.get_json()
    nome = data.get("nome")
    telefone = data.get("telefone")
    carne = int(data.get("carne", 0))
    frango = int(data.get("frango", 0))
    brocolis = int(data.get("brocolis", 0))
    total = (carne + frango + brocolis) * 8
    datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pedidos (nome, telefone, carne, frango, brocolis, total, datahora)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, telefone, carne, frango, brocolis, total, datahora))
    conn.commit()
    conn.close()

    return jsonify({ "status": "success" })

# Login para o admin
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == "pastel123":
            session["logado"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", erro=True)
    return render_template("login.html", erro=False)

# Logout do admin
@app.route("/logout")
def logout():
    session.pop("logado", None)
    return redirect(url_for("login"))

# Painel do admin protegido
@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, telefone, carne, frango, brocolis, total, datahora FROM pedidos ORDER BY datahora DESC")
    pedidos = cursor.fetchall()
    conn.close()
    return render_template("admin.html", pedidos=pedidos)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
