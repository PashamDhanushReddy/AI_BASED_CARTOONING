import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def hashpassword(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")

        hashed = hashpassword(password)
        user = User.query.filter_by(username=username, password_hash=hashed).first()

        if user:
            session["user_id"] = user.id
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html")

        hashed = hashpassword(password)
        new_user = User(username=username, email=email, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")
