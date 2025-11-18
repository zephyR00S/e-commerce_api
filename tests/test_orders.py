def test_create_order(client, user_token):
    # Product
    product = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Watch", "description": "Digital", "price": 100, "stock": 10}
    ).json()

    # Address
    client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "Buyer",
            "phone": "11111",
            "street": "Addr",
            "city": "C",
            "state": "S",
            "pincode": "123456",
            "landmark": None,
            "country": "India",
            "is_primary": True
        }
    )

    # Cart
    client.post(
        "/cart/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"product_id": product["id"], "quantity": 1}
    )

    # Create order
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
