def test_address_create_and_make_primary(client, user_token):
    addr = client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "John Doe",
            "phone": "1234567890",
            "street": "Main St",
            "city": "Kolkata",
            "state": "WB",
            "pincode": "700001",
            "landmark": "Near Park",
            "country": "India",
            "is_primary": True
        }
    )
    assert addr.status_code == 200
    assert addr.json()["is_primary"] is True


def test_create_order_uses_primary_address(client, user_token):
    # Create product
    product = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "TV", "description": "4K", "price": 500, "stock": 5}
    ).json()

    # Add to cart
    client.post(
        "/cart/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"product_id": product["id"], "quantity": 1}
    )

    # Add primary address
    client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "John",
            "phone": "99999",
            "street": "Some Road",
            "city": "City",
            "state": "ST",
            "pincode": "000001",
            "landmark": None,
            "country": "India",
            "is_primary": True
        }
    )

    order = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert order.status_code == 200
    assert order.json()["shipping_city"] == "City"
