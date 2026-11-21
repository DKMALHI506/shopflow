def create_customer(client, email="alice@example.com"):
    response = client.post(
        "/customers/",
        json={"name": "Alice Martin", "email": email},
    )
    assert response.status_code == 201
    return response.json()


def create_order(session_factory, customer_id, status="processing"):
    from app.models import Order

    with session_factory() as db:
        order = Order(
            customer_id=customer_id,
            status=status,
            total="89.99",
            tracking_number="TEST-100",
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order.id


def test_health_endpoint(client):
    api, _ = client
    response = api.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }


def test_create_and_get_customer(client):
    api, _ = client
    customer = create_customer(api)
    response = api.get(f"/customers/{customer['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_duplicate_customer_email_is_rejected(client):
    api, _ = client
    create_customer(api)
    response = api.post(
        "/customers/",
        json={"name": "Another Alice", "email": "alice@example.com"},
    )
    assert response.status_code == 409


def test_customer_can_only_see_own_order(client):
    api, session_factory = client
    customer = create_customer(api)
    order_id = create_order(session_factory, customer["id"])

    own_order = api.get(
        f"/orders/{order_id}?customer_id={customer['id']}"
    )
    other_order = api.get(
        f"/orders/{order_id}?customer_id=9999"
    )

    assert own_order.status_code == 200
    assert other_order.status_code == 404


def test_order_cancellation_needs_confirmation(client):
    api, session_factory = client
    customer = create_customer(api)
    order_id = create_order(session_factory, customer["id"])

    response = api.post(
        f"/orders/{order_id}/cancel",
        json={"customer_id": customer["id"], "confirm": False},
    )

    assert response.status_code == 200
    assert response.json()["eligible"] is True
    assert response.json()["order"] is None


def test_processing_order_can_be_cancelled(client):
    api, session_factory = client
    customer = create_customer(api)
    order_id = create_order(session_factory, customer["id"])

    response = api.post(
        f"/orders/{order_id}/cancel",
        json={"customer_id": customer["id"], "confirm": True},
    )

    assert response.status_code == 200
    assert response.json()["order"]["status"] == "cancelled"


def test_shipped_order_cannot_be_cancelled(client):
    api, session_factory = client
    customer = create_customer(api)
    order_id = create_order(
        session_factory, customer["id"], status="shipped"
    )

    response = api.post(
        f"/orders/{order_id}/cancel",
        json={"customer_id": customer["id"], "confirm": True},
    )

    assert response.status_code == 409


def test_create_support_ticket(client):
    api, session_factory = client
    customer = create_customer(api)
    order_id = create_order(session_factory, customer["id"])

    response = api.post(
        "/tickets/",
        json={
            "customer_id": customer["id"],
            "order_id": order_id,
            "subject": "Delivery issue",
            "description": "The tracking page has not updated.",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert response.json()["priority"] == "high"
