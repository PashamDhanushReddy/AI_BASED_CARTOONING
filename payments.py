from datetime import datetime
from database import Subscription
from flask import Blueprint, flash, redirect, url_for, session
import os
from flask import send_file

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/download")
def download():
    if "user_id" not in session:
        flash("Please login to download images.", "warning")
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    subscription = Subscription.query.filter_by(user_id=user_id).first()
    if not subscription or subscription.end_date < datetime.utcnow():
        flash("Active subscription required to download images.", "danger")
        return redirect(url_for("dashboard.index"))
    
    filepath = session.get('processed_file')
    if filepath and os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash("No processed image available for download.", "danger")
        return redirect(url_for("dashboard.index"))
