from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from books.models import Book
from books.serializers import BookListSerializer


class BookListViewSet(viewsets.ModelViewSet):
    serializer_class = BookListSerializer
    queryset = Book.objects.all()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
