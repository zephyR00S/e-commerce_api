def test_admin_endpoints(client):
    # Create admin
    client.post("/signup", json={
        "email": "admin@example.com",
        "password": "admin123",
        "is_admin": True
    })

    login = client.post(
        "/token",
        data={"username": "admin@example.com", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()

    token = login["access_token"]

    res = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
