from datetime import datetime, date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrows.models import Borrow
from borrows.serializers import BorrowListSerializer, BorrowDetailSerializer

BORROWS_URL = reverse("borrows:borrow-list")


def sample_borrow(user, **params):
    book = Book.objects.create(
        title="Sample",
        author="Name",
        cover="Hard",
        inventory=23,
        daily_fee=2.45,
    )
    defaults = {
        "borrow_date": "2020-05-21",
        "expected_return": "2020-05-30",
        "actual_return": "2020-05-29",
        "book": book,
        "user": user,
    }
    defaults.update(params)
    return Borrow.objects.create(**defaults)


class UnauthenticatedBorrowsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauth_borrow(self):
        res = self.client.get(BORROWS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauth_borrow_create(self):
        res = self.client.post(BORROWS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="example@mail.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_borrows_list(self):
        sample_borrow(self.user)
        response = self.client.get(BORROWS_URL)
        borrows = Borrow.objects.all()
        serializer = BorrowListSerializer(borrows, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_borrows_detail(self):
        borrow = sample_borrow(self.user)
        url = reverse("borrows:borrow-detail", kwargs={"pk": borrow.pk})
        response = self.client.get(url)
        serializer = BorrowDetailSerializer(borrow)

        self.assertEqual(response.data, serializer.data)

    @patch("borrows.views.send_telegram_notification")
    def test_borrows_create_and_telegram_message(self, mock_send_telegram_notification):
        book = Book.objects.create(
            title="Sample",
            author="Name",
            cover="Hard",
            inventory=23,
            daily_fee=2.45,
        )
        payload = {
            "book": book.id,
            "borrow_date": "2020-05-21",
            "expected_return": "2020-05-30",
        }
        res = self.client.post(BORROWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        borrow = Borrow.objects.get(id=res.data["id"])
        for key in payload.keys():
            if key == "book":
                self.assertEqual(payload[key], getattr(borrow, key).id)
            elif key in ["borrow_date", "expected_return"]:
                date_object = datetime.strptime(payload[key], "%Y-%m-%d").date()
                self.assertEqual(date_object, getattr(borrow, key))

        self.assertEqual(mock_send_telegram_notification.call_count, 1)

        expected_message = (
            f"Borrowing create: Book {book.title}, User {self.user.email}"
        )
        mock_send_telegram_notification.assert_called_once_with(expected_message)

    @patch("borrows.serializers.send_telegram_notification")
    def test_return_borrows_and_telegram_message(self, mock_send_telegram_notification):
        book = Book.objects.create(
            title="Sample",
            author="Name",
            cover="Hard",
            inventory=23,
            daily_fee=2.45,
        )
        borrow = Borrow.objects.create(
            book=book,
            user=self.user,
            borrow_date="2020-05-21",
            expected_return="2020-05-30",
        )
        BORROWS_RETURN_URL = reverse(
            "borrows:borrow-borrowing-return", kwargs={"pk": borrow.id}
        )
        payload = {"actual_return": "2020-05-31"}
        res = self.client.post(BORROWS_RETURN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        borrow.refresh_from_db()
        self.assertEqual(
            borrow.actual_return,
            date.today(),
        )

        self.assertEqual(mock_send_telegram_notification.call_count, 1)

        expected_message = (
            f"Borrowing returned: Book {book.title}, User {self.user.email}"
        )
        mock_send_telegram_notification.assert_called_once_with(expected_message)
