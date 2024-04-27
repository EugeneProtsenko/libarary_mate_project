from django.shortcuts import render
from rest_framework import viewsets

from borrows.models import Borrow
from borrows.serializers import (
    BorrowSerializer,
    BorrowListSerializer,
    BorrowDetailSerializer,
    BorrowCreateSerializer,
)


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all().select_related("user", "book")
    serializer_class = BorrowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowListSerializer

        if self.action == "retrieve":
            return BorrowDetailSerializer

        if self.action in ["create", "update", "partial_update"]:
            return BorrowCreateSerializer

        return super().get_serializer_class()

    def perform_create(self, serializer):
        book = serializer.validated_data.get("book")
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)
