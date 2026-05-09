from django.db import models
from django.conf import settings
from laptops.models import Laptop

class Transaction(models.Model):

    ACTION_CHOICES = [
        ("CHECK_IN", "Check In"),
        ("CHECK_OUT", "Check Out"),
        ("TRANSFER", "Transfer"),
    ]

    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name="transactions"
)
    student = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions" )

    previous_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_transactions"
    )
    new_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_transactions"
    )

    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scanned_transactions"
    )

    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.laptop.serial_number} - {self.action_type}"