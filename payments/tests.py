from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrows.models import Borrow
from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentDetailSerializer
from payments.views import payment_success, payment_cancelled

PAYMENTS_URLS = reverse("payments:payment-list")


def sample_payments(user, book, **params):
    borrow = Borrow.objects.create(
        borrow_date="2022-01-21",
        expected_return="2022-01-27",
        actual_return="2022-01-28",
        book=book,
        user=user,
    )

    defaults = {
        "status": "Pending",
        "type": "Payment",
        "borrowing": borrow,
        "session_url": "https://checkout.stripe.com/pay/cs_test_a1mfmMmc3bZbrRpEYvmpO6nPBLs1CwJZcdzTlwvIn6e4Rp6VUUDxnvuzTQ",
        "session_id": "cs_test_a1bz4aB3sXQSupRoy6BP2TrYj95NUmDUIa6SNeBk1otouHabBFG7I1TAjm",
        "money_to_pay": "23.48",
    }

    defaults.update(params)
    return Payment.objects.create(**defaults)


class UnauthenticatedPaymentsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauth_payment(self):
        res = self.client.get(PAYMENTS_URLS)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauth_payment_create(self):
        res = self.client.post(PAYMENTS_URLS)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="example@mail.com", password="password"
        )
        self.book = Book.objects.create(
            title="Sample",
            author="Name",
            cover="Hard",
            inventory=23,
            daily_fee=2.45,
        )
        self.client.force_authenticate(self.user)

    def test_payments_list(self):
        sample_payments(self.user, self.book)
        response = self.client.get(PAYMENTS_URLS)
        payments = Payment.objects.all()
        serializer = PaymentListSerializer(payments, many=True)

        self.assertEqual(response.data["results"], serializer.data)

    def test_payments_detail(self):
        payment = sample_payments(self.user, self.book)
        url = reverse("payments:payment-detail", kwargs={"pk": payment.pk})
        response = self.client.get(url)
        serializer = PaymentDetailSerializer(payment)

        self.assertEqual(response.data, serializer.data)


class PaymentSuccessTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session_id = "test_session_id"
        self.user = get_user_model().objects.create_user(
            email="example@mail.com", password="password"
        )
        self.book = Book.objects.create(
            title="Sample",
            author="Name",
            cover="Hard",
            inventory=23,
            daily_fee=2.45,
        )
        self.borrowing = Borrow.objects.create(
            borrow_date="2022-01-21",
            expected_return="2022-01-27",
            actual_return="2022-01-28",
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url=f"https://checkout.stripe.com/pay/{self.session_id}",
            session_id=self.session_id,
            money_to_pay=23.49,
        )

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_success(self, mock_retrieve):
        # Mock the Stripe Session retrieve call
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_retrieve.return_value = mock_session

        # Create a request object
        request = self.factory.get("/payment_success_url")

        # Call the view function
        response = payment_success(request, self.session_id)

        # Refresh the payment object from the database
        self.payment.refresh_from_db()

        # Check that the payment status was updated
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)

        # Check that the response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Payment was successful!")

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_not_successful(self, mock_retrieve):
        # Mock the Stripe Session retrieve call
        mock_session = MagicMock()
        mock_session.payment_status = "unpaid"
        mock_retrieve.return_value = mock_session

        # Create a request object
        request = self.factory.get("/payment_success_url")

        # Call the view function
        response = payment_success(request, self.session_id)

        # Refresh the payment object from the database
        self.payment.refresh_from_db()

        # Check that the payment status was not updated
        self.assertEqual(self.payment.status, Payment.StatusChoices.PENDING)

        # Check that the response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Payment was not successful.")

    def test_payment_cancel(self):
        request = self.factory.get("/payment_cancelled_url")
        response = payment_cancelled(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode(),
            "Payment was cancelled. You can pay later, but the session is available for only 24 hours.",
        )
