from django.db import models

from borrows.models import Borrow


class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    type = models.CharField(max_length=10, choices=TypeChoices.choices)
    borrowing = models.ForeignKey(Borrow, on_delete=models.CASCADE)
    session_url = models.URLField()
    session_id = models.CharField(max_length=255, blank=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Status {self.status}; Type {self.type}; Session id {self.session_id}"
