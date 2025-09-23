import os
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

from werkzeug.utils import secure_filename

from config import Config
from database import db, User, Transaction
from auth import auth_bp
from payments import payments_bp
from processing import STYLE_MAP
from dashboard import dashboard_bp
from subscriptions import subscriptions_bp  # import subscriptions blueprint

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(payments_bp, url_prefix="/payments")
app.register_blueprint(dashboard_bp)
app.register_blueprint(subscriptions_bp)  # Register subscriptions blueprint

# Diagnostics to confirm the DB and folders at runtime
print("DB URI at runtime:", app.config["SQLALCHEMY_DATABASE_URI"])
print("Uploads folder:", app.config["UPLOAD_FOLDER"])
print("Processed folder:", app.config["PROCESSED_FOLDER"])

# Initialize database
db.init_app(app)

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["PROCESSED_FOLDER"], exist_ok=True)

# Create tables at startup within app context (Flask 3.x)
with app.app_context():
    db.create_all()
    # Optional: verify tables exist by performing a harmless query
    try:
        _ = User.query.first()
        _ = Transaction.query.first()
        print("DB check OK: users/transactions tables are accessible.")
    except Exception as e:
        print("DB check failed:", e)

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "user_id" not in session:
            flash("Please login to process images.", "warning")
            return redirect(url_for("auth.login"))

        if "image" not in request.files:
            flash("No file part", "danger")
            return redirect(url_for("index"))

        file = request.files["image"]
        style = request.form.get("style")

        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(url_for("index"))

        if not style or style not in STYLE_MAP:
            flash("Please select a valid style", "danger")
            return redirect(url_for("index"))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            )
            try:
                file.save(save_path)
            except Exception as e:
                flash(f"Failed to save upload: {e}", "danger")
                return redirect(url_for("index"))

            image = cv2.imdecode(np.fromfile(save_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                flash("Failed to read the uploaded image.", "danger")
                return redirect(url_for("index"))

            try:
                processed = STYLE_MAP[style](image)
            except Exception as e:
                flash(f"Processing failed: {e}", "danger")
                return redirect(url_for("index"))

            processed_name = (
                f"cartoonized_{style.lower().replace(' ', '_')}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            processed_path = os.path.join(app.config["PROCESSED_FOLDER"], processed_name)

            try:
                cv2.imwrite(processed_path, processed)
            except Exception as e:
                flash(f"Failed to write processed image: {e}", "danger")
                return redirect(url_for("index"))

            session["original_file"] = save_path
            session["processed_file"] = processed_path
            session["selected_style"] = style

            return redirect(url_for("result"))

        flash("Invalid file type. Allowed: png, jpg, jpeg", "danger")

    return render_template("index.html")

@app.route("/result")
def result():
    if "processed_file" not in session or "original_file" not in session:
        flash("No processed image found.", "danger")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        original_path=os.path.relpath(session["original_file"], start=os.path.dirname(__file__)),
        processed_path=os.path.relpath(session["processed_file"], start=os.path.dirname(__file__)),
        style=session.get("selected_style", "Unknown")
    )

@app.route("/static_image/")
def static_image():
    from flask import request, send_file
    file_path = request.args.get("file_path")
    if not file_path:
        flash("File path missing", "danger")
        return redirect(url_for("index"))
    abs_path = os.path.join(os.path.dirname(__file__), file_path)
    return send_file(abs_path)

if __name__ == "__main__":
    # Disable reloader temporarily to avoid double-process issues on Windows during setup
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)
