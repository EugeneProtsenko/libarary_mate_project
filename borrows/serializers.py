from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    def validate_return_date(self, value):
        if value < datetime.now().date():
            raise ValidationError(detail="The return date cannot be in the past")
        return value


class BorrowReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
        )
        read_only_fields = ("id", "borrow_date", "expected_return")

    @transaction.atomic
    def validate(self, attrs):
        borrowing = self.instance
        if borrowing.actual_return is not None:
            raise ValidationError(detail="Borrowing has been already returned.")
        return super().validate(attrs=attrs)

    def update(self, instance, validated_data):
        book = instance.book
        instance.actual_return = datetime.now().date()
        instance.save()
        book.inventory += 1
        book.save()
        return instance
