def test_create_and_list_products(client, user_token):
    res = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Laptop",
            "description": "Fast laptop",
            "price": 999.99,
            "stock": 5
        }
    )
    assert res.status_code == 200

    res2 = client.get("/products/")
    assert len(res2.json()) == 1


def test_get_single_product(client, user_token):
    # Create
    product = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Phone",
            "description": "Smart phone",
            "price": 499.99,
            "stock": 10
        }
    ).json()

    # Fetch
    res = client.get(f"/products/{product['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Phone"
