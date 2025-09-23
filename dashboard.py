from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database import User, Transaction, Subscription, db
from werkzeug.utils import secure_filename
import os
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

def subscription_active(subscription):
    if subscription and subscription.end_date and subscription.end_date > datetime.utcnow():
        return True
    return False

@dashboard_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Please login to access dashboard.", "warning")
        return redirect(url_for("auth.login"))
    user = User.query.get(session["user_id"])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))
    if user.username == "admin":
        users = User.query.all()
        user_data = []
        for u in users:
            transactions = Transaction.query.filter_by(user_id=u.id).order_by(Transaction.created_at.desc()).all()
            subscription = Subscription.query.filter_by(user_id=u.id).first()
            user_data.append({
                "user": u,
                "transactions": transactions,
                "subscription": subscription
            })
        return render_template("dashboard_admin.html", user=user, user_data=user_data)
    # For normal users
    edit_mode = request.args.get("edit") == "true"
    if request.method == "POST":
        # Update profile logic
        username = request.form.get("username")
        email = request.form.get("email")
        profile_pic = request.files.get("profile_pic")
        if username:
            user.username = username
        if email:
            user.email = email
        if profile_pic and profile_pic.filename != "":
            filename = secure_filename(profile_pic.filename)
            pic_path = os.path.join("static/uploads/profile_pics", filename)
            os.makedirs(os.path.dirname(pic_path), exist_ok=True)
            profile_pic.save(pic_path)
            user.profile_picture = "uploads/profile_pics/" + filename
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("dashboard.index"))
    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.created_at.desc()).all()
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    active_sub = subscription_active(subscription)
    return render_template("dashboard.html",
                           user=user,
                           transactions=transactions,
                           subscription=subscription,
                           active_subscription=active_sub,
                           edit_mode=edit_mode)
