# from django.db import models
# from users.models import User


# class Laptop(models.Model):

#     STATUS_CHOICES = (
#         ('in_library', 'In Library'),
#         ('checked_out', 'Checked Out'),
#         ('temporary', 'Temporary Access'),
#     )
#     owner = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="owned_laptops"
#     )

#     model_name = models.CharField(max_length=100)
#     serial_number = models.CharField(max_length=100, unique=True)

#     #  QR system (we will generate later)
#     qr_data = models.TextField()

#     # tracking status
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='in_library'
#     )

#     # temporary borrower (your “temporary access” feature)
#     temp_holder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
#                                     related_name="borrowed_laptops"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.model_name} ({self.serial_number})"