from django.urls import path
from .views import download_qr, my_laptop

urlpatterns = [
    path('download_qr/<int:laptop_id>/', download_qr),
    path("my_laptop/", my_laptop, name="my_laptop"),
]
