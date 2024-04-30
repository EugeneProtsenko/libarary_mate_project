import stripe
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, mixins, settings
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

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


# class CreateStripeSessionView(APIView):
#     def post(self, request, *args, **kwargs):
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         book_id = request.data.get("book_id")
#
#         # Fetch the book from the database
#         try:
#             book = Book.objects.get(id=book_id)
#         except Book.DoesNotExist:
#             return Response({"error": "Book not found"}, status=404)
#
#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             line_items=[
#                 {
#                     "price_data": {
#                         "currency": "usd",
#                         "product_data": {
#                             "name": book.title,
#                         },
#                         "daily_fee": book.daily_fee,
#                     },
#                     "quantity": 1,
#                 }
#             ],
#             mode="payment",
#             success_url=request.build_absolute_uri(reverse("payment_success")),
#             cancel_url=request.build_absolute_uri(reverse("payment_cancelled")),
#         )
#
#         return Response(
#             {
#                 "session_id": session.id,
#                 "session_url": f"https://checkout.stripe.com/pay/{session.id}",
#             }
#         )


def payment_success(request):
    return HttpResponse("Payment was successful!")


def payment_cancelled(request):
    return HttpResponse("Payment was cancelled.")
