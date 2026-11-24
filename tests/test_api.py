def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login(client):
    import uuid
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    r1 = client.post("/api/auth/register", json={"name": "A", "email": email, "password": "password123"})
    assert r1.status_code == 200
    r2 = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_login_wrong_password(client):
    import uuid
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"name": "A", "email": email, "password": "password123"})
    r = client.post("/api/auth/login", json={"email": email, "password": "wrongpass"})
    assert r.status_code == 401


def test_history_requires_auth(client):
    resp = client.get("/api/analysis/history")
    assert resp.status_code == 401
