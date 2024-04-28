from celery import shared_task
from django.utils import timezone
from .models import Borrow
from telegram_helper import (
    send_telegram_notification,
)  # assuming you have a function for this


@shared_task
def check_overdue_borrowings():
    overdue_borrowings = Borrow.objects.filter(
        expected_return__lte=timezone.now().date(), actual_return=None
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = f"Borrowing overdue: Book {borrowing.book.title}, User {borrowing.user.email}"
            send_telegram_notification(message)
    else:
        send_telegram_notification("No borrowings overdue today!")
