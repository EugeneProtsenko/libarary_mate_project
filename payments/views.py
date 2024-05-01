import stripe
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from library_project_final import settings

from books.models import Book
from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.all().select_related("borrowing")
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return PaymentDetailSerializer
        else:
            return PaymentListSerializer


@transaction.atomic
def payment_success(request, session_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment = Payment.objects.get(session_id=session_id)
        payment.status = Payment.StatusChoices.PAID
        payment.save()

        return HttpResponse("Payment was successful!")
    else:
        return HttpResponse("Payment was not successful.")


def payment_cancelled(request):
    return HttpResponse(
        "Payment was cancelled. You can pay later, but the session is available for only 24 hours."
    )
