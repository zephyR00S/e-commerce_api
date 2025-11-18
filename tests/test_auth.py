def test_signup_and_login(client):
    res = client.post("/signup", json={
        "email": "a@b.com",
        "password": "pass123"
    })
    assert res.status_code == 200

    token_res = client.post("/token",
        data={"username": "a@b.com", "password": "pass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert "access_token" in token_res.json()
