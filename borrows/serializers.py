from django.db import transaction
from rest_framework import serializers

from borrows.models import Borrow


class BorrowSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrow
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book",
            "user",
            "is_active",
        )

    def get_is_active(self, obj):
        return obj.actual_return is None


class BorrowListSerializer(BorrowSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)

    class Meta:
        model = Borrow
        fields = (
            "id",
            "book_title",
            "book_author",
        )


class BorrowDetailSerializer(BorrowSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)
    book_cover = serializers.CharField(source="book.cover", read_only=True)
    book_inventory = serializers.CharField(source="book.inventory", read_only=True)
    daily_fee = serializers.CharField(source="book.daily_fee", read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrow
        fields = (
            "id",
            "book_title",
            "book_author",
            "book_cover",
            "book_inventory",
            "daily_fee",
            "is_active",
        )

    def get_is_active(self, obj):
        return obj.actual_return is None


class BorrowCreateSerializer(BorrowDetailSerializer):
    class Meta:
        model = Borrow
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book_title",
            "book_author",
            "daily_fee",
        )

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError("This book is currently out of stock.")
        return book
