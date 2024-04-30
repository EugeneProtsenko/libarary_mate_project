from rest_framework import routers
from django.urls import path, include

from payments import views
from payments.views import PaymentViewSet

router = routers.DefaultRouter()

router.register("", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-cancelled/", views.payment_cancelled, name="payment_cancelled"),
]

app_name = "payments"
