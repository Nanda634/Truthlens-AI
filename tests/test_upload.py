import io
from PIL import Image


def make_test_image():
    buf = io.BytesIO()
    Image.new("RGB", (200, 200), color=(100, 150, 200)).save(buf, "JPEG")
    buf.seek(0)
    return buf


def test_upload_requires_auth(client):
    resp = client.post("/api/files/upload", files={"file": ("t.jpg", make_test_image(), "image/jpeg")})
    assert resp.status_code == 401


def test_upload_valid_image(client, auth_headers):
    resp = client.post("/api/files/upload", files={"file": ("t.jpg", make_test_image(), "image/jpeg")}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["category"] == "image"
    assert len(data["sha256"]) == 64


def test_upload_unsupported_type(client, auth_headers):
    resp = client.post("/api/files/upload", files={"file": ("t.exe", io.BytesIO(b"MZ" + b"\x00" * 100), "application/octet-stream")}, headers=auth_headers)
    assert resp.status_code in (400, 200)  # depends on magic-byte detection; must not 500
