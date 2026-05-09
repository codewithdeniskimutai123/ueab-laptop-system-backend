from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        "laptop",
        "student",
        "action_type",
        "previous_holder",
        "new_holder",
        "scanned_by",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "action_type",
        "created_at",
    )

    search_fields = (
        "laptop__serial_number",
        "student__email",
        "student__student_id",
    )

    ordering = ("-created_at",)

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        # Only Admin + Security
        if db_field.name == "scanned_by":
            kwargs["queryset"] = User.objects.filter(
                role__in=["ADMIN", "SECURITY"]
            )

        # Only Students
        elif db_field.name in [
            "student",
            "previous_holder",
            "new_holder",
        ]:
            kwargs["queryset"] = User.objects.filter(
                role="STUDENT"
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )