from django.urls import path
from . import views

urlpatterns = [
    path("register_laptop/", views.register_laptop, name="admin_register_laptop"),
    path("modify_role/", views.admin_modify_user_role, name="admin_modify_role"),
    path("analytics/", views.admin_global_analytics, name="admin_global_analytics"),
    path("delete_laptop/<int:laptop_id>/", views.admin_delete_laptop, name="admin_delete_laptop"),
    path("delete_user/<int:user_id>/", views.admin_delete_user, name="admin_delete_user"),
    path("list_laptops/", views.list_laptops, name="list_laptops"),


]
