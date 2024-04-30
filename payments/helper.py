import stripe

from library_project_final import settings
from payments.models import Payment

from datetime import datetime


def calculate_total_price(borrowing):
    return_date = (
        borrowing.actual_return if borrowing.actual_return else datetime.now().date()
    )
    num_days = (return_date - borrowing.borrow_date).days
    total_price = num_days * borrowing.book.daily_fee

    if borrowing.expected_return < return_date:
        total_price += borrowing.book.late_fee

    return total_price


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing):
    # Calculate the total price of borrowing
    total_price = calculate_total_price(borrowing)

    # Create a new Stripe Session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/api/payments/payment-success/",  # {CHECKOUT_SESSION_ID}
        cancel_url="http://localhost:8000/api/payments/payment_cancelled",
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=f"https://checkout.stripe.com/pay/{session.id}",
        session_id=session.id,
        money_to_pay=total_price,
    )

    return payment
