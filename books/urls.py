from rest_framework import routers
from django.urls import path, include

from books.views import BookListViewSet

router = routers.DefaultRouter()

router.register("books", BookListViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "books"
