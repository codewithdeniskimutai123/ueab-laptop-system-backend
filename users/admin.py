from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "student_id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "role",
        "is_staff",
        "is_active",
        "profile_photo",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {
            "fields": ("student_id", "phone_number", "role", "profile_photo")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Info", {
            "fields": ("student_id", "phone_number", "role", "profile_photo")
        }),
    )


admin.site.register(User, CustomUserAdmin)
