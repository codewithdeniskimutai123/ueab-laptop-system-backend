from django.urls import path
from .views import (
    admin_overview,
    admin_laptops,
    admin_laptop_detail,
    admin_users,
    admin_user_detail,
    admin_transactions,
    admin_transaction_detail,
)


urlpatterns = [
    path("admin_overview/", admin_overview, name="admin_overview"),
    #all laptops
    path("laptops/", admin_laptops, name="admin-laptops"),
    path("laptops/<int:laptop_id>/", admin_laptop_detail, name="admin-laptop-detail"),
    path("users/", admin_users, name="admin-users"),
    path("users/<int:user_id>/", admin_user_detail, name="admin-user-detail"),
    path("transactions/", admin_transactions, name="admin-transactions"),
    path( "transactions/<int:transaction_id>/", admin_transaction_detail, name="admin-transaction-detail"),

]