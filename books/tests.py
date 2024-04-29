from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookListSerializer

BOOKS_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample",
        "author": "Name",
        "cover": "Hard",
        "inventory": 23,
        "daily_fee": 2.45,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_books_list(self):
        sample_book()
        response = self.client.get(BOOKS_URL)
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_unauth_book(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauth_book_create(self):
        res = self.client.post(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="example@mail.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_books_list(self):
        sample_book()
        response = self.client.get(BOOKS_URL)
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_create_book_by_user(self):
        res = self.client.post(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authorized_book(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AdminUserBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="password"
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_book_by_admin(self):
        """Test creating a book by an admin user"""
        payload = {
            "title": "Admin Book",
            "author": "Admin Author",
            "cover": "Hard",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))
