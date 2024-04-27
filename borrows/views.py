from django.shortcuts import render
from rest_framework import viewsets

from borrows.models import Borrow
from borrows.serializers import (
    BorrowSerializer,
    BorrowListSerializer,
    BorrowDetailSerializer,
)


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all()
    serializer_class = BorrowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowListSerializer

        if self.action == "retrieve":
            return BorrowDetailSerializer

        return BorrowSerializer
