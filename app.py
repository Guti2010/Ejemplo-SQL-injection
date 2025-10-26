from flask import Flask, render_template, request
import sqlite3, os

DB_PATH = os.environ.get("DB_PATH", "app.db")
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
    """)
    # Semilla de usuarios
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("alice", "s3cret"))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login-vuln", methods=["GET", "POST"])
def login_vuln():
    if request.method == "GET":
        return render_template("login.html",
                               title="Login (VULNERABLE)",
                               route_name="login-vuln",
                               hint="Ejemplo de ataque: usuario = admin' OR 1=1 --  (cualquier password).")
    user = request.form.get("user", "")
    pwd  = request.form.get("pass", "")
    # VULNERABLE: concatenación de strings → inyec. SQL
    q = f"SELECT id, username FROM users WHERE username='{user}' AND password='{pwd}'"
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(q)  # ejecuta SQL inyectable
        row = cur.fetchone()
        conn.close()
        if row:
            return render_template("login.html",
                                   title="Login (VULNERABLE)",
                                   route_name="login-vuln",
                                   success=f"Bienvenido, {row[1]}",
                                   query=q)
        else:
            return render_template("login.html",
                                   title="Login (VULNERABLE)",
                                   route_name="login-vuln",
                                   error="Acceso denegado",
                                   query=q)
    except Exception as e:
        return render_template("login.html",
                               title="Login (VULNERABLE)",
                               route_name="login-vuln",
                               error=f"Error SQL expuesto: {e}",
                               query=q)

@app.route("/login-safe", methods=["GET", "POST"])
def login_safe():
    if request.method == "GET":
        return render_template("login.html",
                               title="Login (SEGURO)",
                               route_name="login-safe",
                               hint="Defensa: consultas parametrizadas (placeholders ?).")
    user = request.form.get("user", "")
    pwd  = request.form.get("pass", "")
    # SEGURO: parámetros → datos ≠ código
    q = "SELECT id, username FROM users WHERE username=? AND password=?"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(q, (user, pwd))
    row = cur.fetchone()
    conn.close()
    if row:
        return render_template("login.html",
                               title="Login (SEGURO)",
                               route_name="login-safe",
                               success=f"Bienvenido, {row[1]} ",
                               query=q)
    else:
        return render_template("login.html",
                               title="Login (SEGURO)",
                               route_name="login-safe",
                               error="Acceso denegado",
                               query=q)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
