# from django.db import models
# from users.models import User
# from laptops.models import Laptop


# class TemporaryAccess(models.Model):

#     STATUS_CHOICES = (
#         ('active', 'Active'),
#         ('returned', 'Returned'),
#         ('expired', 'Expired'),
#     )

#     # owner giving access
#     giver = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="given_access"
#     )

#     # student receiving temporary access
#     receiver = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="received_access"
#     )

#     # laptop being shared
#     laptop = models.ForeignKey(
#         Laptop,
#         on_delete=models.CASCADE,
#         related_name="temporary_accesses"
#     )

#     # timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(null=True, blank=True)

#     # status tracking
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='active'
#     )

#     # optional notes
#     remarks = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.giver.username} → {self.receiver.username}"