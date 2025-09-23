import razorpay
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from database import db, Transaction

subscriptions_bp = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")

def require_login():
    return "user_id" in session

# Initialize razorpay client globally once with current_app config
client = None

def get_razorpay_client():
    global client
    if client is None:
        client = razorpay.Client(auth=(current_app.config["RAZORPAY_KEY_ID"], current_app.config["RAZORPAY_KEY_SECRET"]))
    return client

@subscriptions_bp.route("/plans")
def plans():
    if not require_login():
        flash("Please login to subscribe.", "warning")
        return redirect(url_for("auth.login"))
    plans = {
        "weekly": current_app.config["RAZORPAY_PLAN_WEEKLY"],
        "monthly": current_app.config["RAZORPAY_PLAN_MONTHLY"],
        "yearly": current_app.config["RAZORPAY_PLAN_YEARLY"],
    }
    return render_template("subscriptions/plans.html", plans=plans, razorpay_key=current_app.config["RAZORPAY_KEY_ID"])

@subscriptions_bp.route("/create_subscription", methods=["POST"])
def create_subscription():
    if not require_login():
        return jsonify({"error": "Login required"}), 401

    plan_key = request.form.get("plan_key")
    plan_map = {
        "weekly": current_app.config["RAZORPAY_PLAN_WEEKLY"],
        "monthly": current_app.config["RAZORPAY_PLAN_MONTHLY"],
        "yearly": current_app.config["RAZORPAY_PLAN_YEARLY"],
    }
    plan_id = plan_map.get(plan_key)
    if not plan_id:
        return jsonify({"error": "Invalid plan"}), 400

    try:
        client = get_razorpay_client()

        user_id = session["user_id"]
        subscription_data = {
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": 12 if plan_key == "monthly" else (52 if plan_key == "weekly" else 1),
            "notes": {"user_id": str(user_id)}
        }
        subscription = client.subscription.create(subscription_data)

        txn = Transaction(
            user_id=user_id,
            transaction_id=subscription["id"],
            amount=0,
            status="created",
        )
        db.session.add(txn)
        db.session.commit()
        return jsonify({"subscription_id": subscription["id"], "razorpay_key": current_app.config["RAZORPAY_KEY_ID"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@subscriptions_bp.route("/success", methods=["POST"])
def payment_success():
    data = request.form.to_dict()
    try:
        client = get_razorpay_client()
        razorpay.utils.verify_payment_signature(data)
    except razorpay.errors.SignatureVerificationError:
        flash("Payment signature verification failed.", "danger")
        return redirect(url_for("subscriptions.plans"))

    subscription_id = data.get("razorpay_subscription_id")
    txn = Transaction.query.filter_by(transaction_id=subscription_id).first()
    if txn:
        txn.status = "completed"
        db.session.commit()
        session["payment_ok"] = True
        flash("Subscription successful! Thank you.", "success")
        return redirect(url_for("dashboard.index"))
    flash("Subscription transaction not found.", "danger")
    return redirect(url_for("subscriptions.plans"))
