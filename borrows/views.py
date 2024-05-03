from datetime import datetime

from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payments.helper import create_stripe_session
from telegram_helper import send_telegram_notification

from borrows.models import Borrow

# from borrows.permissions import IsAdminOrIsSelf
from borrows.serializers import (
    BorrowSerializer,
    BorrowListSerializer,
    BorrowDetailSerializer,
    BorrowCreateSerializer,
    BorrowReturnSerializer,
)


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all().select_related("user", "book")
    serializer_class = BorrowSerializer
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    @staticmethod
    def _params_to_bool(qs: str) -> bool:
        return qs.lower() == "true"

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.query_params.get("user_id")
        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = self._params_to_bool(is_active)
            if is_active_bool:
                queryset = queryset.filter(actual_return__isnull=True)
            else:
                queryset = queryset.filter(actual_return__isnull=False)

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset

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
        message = f"Borrowing create: Book {book.title}, User {serializer.instance.user.email}"
        send_telegram_notification(message)
        create_stripe_session(serializer.instance)

    @extend_schema(
        request=BorrowReturnSerializer,
        responses={200: BorrowReturnSerializer(many=True)},
        methods=["POST"],
        description="Returns a book by its ID.",
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="return",
        serializer_class=BorrowReturnSerializer,
    )
    def borrowing_return(self, request, pk=None):
        """
        Returns a book by its ID.
        """
        borrowing = self.get_object()
        book = borrowing.book
        actual_return = datetime.now().date()

        serializer_update = BorrowReturnSerializer(
            borrowing,
            context={"request": self.request},
            data={"actual_return": actual_return},
            partial=True,
        )
        serializer_update.is_valid(raise_exception=True)
        serializer_update.save()
        return Response({"status": "borrowing returned"})

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter borrows by user ID",
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter borrows by active status",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Returns a list of all the borrows.
        """
        return super().list(request, *args, **kwargs)
