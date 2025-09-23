import os
import io
import numpy as np
import cv2
from app import app, db

def make_image_bytes():
    img = np.random.randint(0,255,(128,128,3),dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", img)
    return io.BytesIO(buf.tobytes())

def test_home_get():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200

def test_auth_cycle():
    client = app.test_client()
    with app.app_context():
        db.create_all()

    # Register
    r = client.post("/auth/register", data={
        "username":"tester",
        "email":"tester@example.com",
        "password":"TestPass123"
    }, follow_redirects=True)
    assert r.status_code == 200

    # Login
    r = client.post("/auth/login", data={
        "username":"tester",
        "password":"TestPass123"
    }, follow_redirects=True)
    assert r.status_code == 200

def test_upload_without_login():
    client = app.test_client()
    data = {
        "style": "Classic Cartoon",
        "image": (make_image_bytes(), "test.jpg")
    }
    r = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert r.status_code == 200
    assert b"Please login to process images." in r.data
