from flask import Flask, request, redirect, url_for, session, render_template
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Hardcoded accounts (local@domain format)
USERS = {
    "elon@x": "musk",
    "andy@airbnb": "kieckhefer",
    "ericka@nm": "/#Batwinkski .",
}

@app.route("/", methods=["GET"])
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if email in USERS and USERS[email] == password:
            session["user"] = email
            return redirect(url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8007)
