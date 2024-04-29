from django.test import TestCase
from rest_framework.reverse import reverse

BORROWS_URL = reverse("borrows:borrows-list")


def sample_borrow():
    defaults = {}
