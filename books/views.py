from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from books.models import Book
from books.serializers import BookListSerializer


class BookListViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """

    serializer_class = BookListSerializer
    queryset = Book.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Returns a list of all the books.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a book by its ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        """
        Returns the list of permissions that this view requires.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
