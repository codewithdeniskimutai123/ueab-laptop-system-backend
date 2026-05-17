from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Laptop

User = get_user_model()
@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "brand",
        "serial_number",
        "owner",
        "current_holder",
        "is_inside_library",
        "is_checked_out",
        "created_at",
    )

    list_filter = (
        "brand",
        "is_inside_library",
        "is_checked_out",
    )

    search_fields = (
        "serial_number",
        "owner__email",
        "owner__student_id",
    )

    ordering = ("-created_at",)

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        if db_field.name in [
            "owner",
            "current_holder"
        ]:
            kwargs["queryset"] = User.objects.filter(
                role="STUDENT"
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )