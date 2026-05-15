from django.urls import path
from . import views

urlpatterns = [
    path("preview/", views.preview_transaction, name="preview_transaction"),
    path("confirm/", views.confirm_transaction, name="confirm_transaction"),
    path("transfer/", views.transfer_laptop, name="transfer_laptop"),
    path("my_transactions/", views.student_transactions_list, name="my_transactions"),
    path("recent_transactions/", views.recent_transactions, name="recent_transactions"),
    path("scan_qr/", views.scan_qr, name="scan_qr"),
]