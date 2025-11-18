def test_add_to_cart_and_view(client, user_token):
    # Create product
    product = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Mouse", "description": "Wireless", "price": 50, "stock": 20}
    ).json()

    # Add to cart
    add = client.post(
        "/cart/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"product_id": product["id"], "quantity": 2}
    )
    assert add.status_code == 200

    # View cart
    view = client.get("/cart/", headers={"Authorization": f"Bearer {user_token}"})
    assert len(view.json()["items"]) == 1


def test_update_and_remove_cart(client, user_token):
    product = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Keyboard", "description": "RGB", "price": 80, "stock": 10}
    ).json()

    client.post(
        "/cart/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"product_id": product["id"], "quantity": 1}
    )

    update = client.put(
        f"/cart/{product['id']}?quantity=3",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert update.status_code == 200

    delete = client.delete(
        f"/cart/{product['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert delete.status_code == 200
