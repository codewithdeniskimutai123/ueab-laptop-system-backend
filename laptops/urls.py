from django.urls import path
from .views import register_laptop, download_qr, my_laptop

urlpatterns = [
    path('register/', register_laptop, name='register_laptop'),
    path('download_qr/<int:laptop_id>/', download_qr),
    path("my_laptop/", my_laptop, name="my_laptop"),
]
