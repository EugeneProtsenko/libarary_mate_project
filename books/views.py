from django.shortcuts import render
from rest_framework import viewsets

from books.models import Book
from books.serializers import BookListSerializer


class BookListViewSet(viewsets.ModelViewSet):
    serializer_class = BookListSerializer
    queryset = Book.objects.all()
