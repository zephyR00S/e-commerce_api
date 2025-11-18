def test_mock_payment_and_refund(client, user_token):
    # Create order pre-requisites
    product = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Bag", "description": "Travel", "price": 40, "stock": 10}
    ).json()

    client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "User",
            "phone": "00000",
            "street": "St",
            "city": "City",
            "state": "State",
            "pincode": "111111",
            "landmark": "",
            "country": "India",
            "is_primary": True
        }
    )

    client.post(
        "/cart/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"product_id": product["id"], "quantity": 1}
    )

    order = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {user_token}"}
    ).json()

    # Pay
    pay = client.post(f"/orders/{order['id']}/pay",
        headers={"Authorization": f"Bearer {user_token}"})
    assert pay.json()["status"] == "Paid"

    # Refund
    refund = client.post(f"/orders/{order['id']}/refund",
        headers={"Authorization": f"Bearer {user_token}"})
    assert refund.json()["status"] == "Refunded"
