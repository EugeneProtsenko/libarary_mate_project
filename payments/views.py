from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
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
