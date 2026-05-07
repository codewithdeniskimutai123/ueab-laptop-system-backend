# from django.db import models
# from users.models import User
# from laptops.models import Laptop


# class Transaction(models.Model):

#     ACTION_CHOICES = (
#         ('check_in', 'Check In'),
#         ('check_out', 'Check Out'),
#         ('temporary_access', 'Temporary Access'),
#         ('registration', 'Laptop Registration'),
#     )

#     # who performed the action
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="transactions"
#     )

#     # related laptop (can be null for registration actions)
#     laptop = models.ForeignKey(
#         Laptop,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="transactions"
#     )

#     # type of action
#     action = models.CharField(max_length=30, choices=ACTION_CHOICES)

#     # timestamp of action
#     timestamp = models.DateTimeField(auto_now_add=True)

#     # optional notes (VERY useful for security)
#     remarks = models.TextField(blank=True, null=True)
# # 
#     def __str__(self):
#         return f"{self.user.username} - {self.action}"