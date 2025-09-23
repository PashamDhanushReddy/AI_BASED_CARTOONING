# AI Toonify Subscription App

A Flask-based web application that allows users to upload images, apply cartoon/AnimeGAN/Sketch effects, and manage subscriptions with payment integration.

## Features

  - User registration, login, profile update
  - Image upload and processing with cartoon, sketch, pencil, and advanced AnimeGAN filters
  - Subscription management (weekly/monthly/yearly) via Razorpay
  - Payment gateway integration (Razorpay)
  - Admin dashboard to view and manage users, transactions, and subscriptions
  - Secure download of processed images for subscribed users
  - Model pre-download and caching for fast inference

## Tech Stack

  - Python (Flask)
  - SQLAlchemy (SQLite)
  - OpenCV (cv2), NumPy
  - Razorpay Python SDK
  - Torch, torchvision (AnimeGAN)
  - Pillow (PIL)
  - HTML/CSS/Jinja2 templates

## Getting Started

1. **Install dependencies**

   See `requirements.txt` below.

2. **Environment Variables**

   - Set `SECRET_KEY` for Flask security.
   - Set Razorpay credentials:
     - `RAZORPAY_KEY_ID`
     - `RAZORPAY_KEY_SECRET`
     - (Optional) Razorpay Plan IDs for weekly, monthly, yearly subscriptions.

3. **Run the application:**
    
    - App runs at http://localhost:8000

4. **Model Pre-download (Optional, recommended for AnimeGAN):**

    
## Folder Structure
  
  - `app.py` — Flask app entry
  - `auth.py`, `dashboard.py`, `subscriptions.py`, `payments.py` — app modules
  - `processing.py` — image transform functions
  - `predownload_models.py` — model fetch utility
  - `database.py` — SQLAlchemy ORM models
  - `templates/` — HTML templates
  - `static/` — CSS and assets
  
## License

MIT

