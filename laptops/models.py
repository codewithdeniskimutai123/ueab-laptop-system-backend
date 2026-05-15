import json
import qrcode

from io import BytesIO

from django.db import models
from django.core.files import File
from django.contrib.auth import get_user_model

User = get_user_model()


class Laptop(models.Model):

    BRAND_CHOICES = [
        ("HP", "HP"),
        ("DELL", "Dell"),
        ("LENOVO", "Lenovo"),
        ("APPLE", "Apple"),
        ("OTHER", "Other"),
    ]
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_laptops"
    )

    current_holder = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="held_laptops"
    )

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    serial_number = models.CharField(max_length=100, unique=True )
    qr_code = models.ImageField(upload_to="laptop_qr/", null=True, blank=True)
    is_inside_library = models.BooleanField(default=False)
    is_checked_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):

       
        if not self.pk and not self.current_holder:
            self.current_holder = self.owner

        super().save(*args, **kwargs)

        if not self.qr_code:

            qr_data = {
                "laptop_id": self.id,

                "owner": {
                    "name": f"{self.owner.first_name} {self.owner.last_name}",
                    "student_id": self.owner.student_id,
                    "email": self.owner.email,
                },

                "current_holder": {
                    "name": f"{self.current_holder.first_name} {self.current_holder.last_name}",
                    "student_id": self.current_holder.student_id,
                    "email": self.current_holder.email,
                },

                "brand": self.brand,
                "serial_number": self.serial_number,
            }

            qr_image = qrcode.make(json.dumps(qr_data))

            buffer = BytesIO()

            qr_image.save(buffer)

            file_name = f"{self.serial_number}.png"

            self.qr_code.save(
                file_name,
                File(buffer),
                save=False
            )

            super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.brand} ({self.serial_number})"