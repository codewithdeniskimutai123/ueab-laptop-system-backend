from django.urls import path
from .views import register_laptop, download_qr

urlpatterns = [
    path('register/', register_laptop, name='register_laptop'),
    path('download_qr/<int:laptop_id>/', download_qr),
]
