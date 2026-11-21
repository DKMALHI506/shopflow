from decimal import Decimal

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Customer, Order


def seed() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        sample_customers = [
            ("Alice Martin", "alice@example.com"),
            ("David Smith", "david@example.com"),
            ("Emma Wilson", "emma@example.com"),
        ]

        customers_by_email: dict[str, Customer] = {}

        for name, email in sample_customers:
            customer = db.scalar(
                select(Customer).where(Customer.email == email)
            )
            if customer is None:
                customer = Customer(name=name, email=email)
                db.add(customer)
                db.flush()
            customers_by_email[email] = customer

        sample_orders = [
            ("alice@example.com", "processing", Decimal("89.99"), "TRK1001"),
            ("alice@example.com", "shipped", Decimal("149.50"), "TRK1002"),
            ("david@example.com", "pending", Decimal("49.99"), None),
            ("emma@example.com", "delivered", Decimal("220.00"), "TRK1004"),
        ]

        for email, order_status, total, tracking_number in sample_orders:
            customer = customers_by_email[email]
            existing = db.scalar(
                select(Order).where(
                    Order.customer_id == customer.id,
                    Order.tracking_number == tracking_number
                    if tracking_number is not None
                    else Order.status == order_status,
                )
            )

            if existing is None:
                db.add(
                    Order(
                        customer_id=customer.id,
                        status=order_status,
                        total=total,
                        tracking_number=tracking_number,
                    )
                )

        db.commit()

    print("Sample customers and orders are ready.")


if __name__ == "__main__":
    seed()
