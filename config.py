import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'toonify.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # Razorpay
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_RIEJdlDrWgTrU8")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "Q8f0inOxLsO67u5PPOdzfFjZ")
    RAZORPAY_PLAN_WEEKLY = os.getenv("RAZORPAY_PLAN_WEEKLY", "plan_RIFXgDGJuwjU0p")
    RAZORPAY_PLAN_MONTHLY = os.getenv("RAZORPAY_PLAN_MONTHLY", "plan_RIFYrp0oVpxa9b")
    RAZORPAY_PLAN_YEARLY = os.getenv("RAZORPAY_PLAN_YEARLY", "plan_RIFZL8QyXuYFmI")
