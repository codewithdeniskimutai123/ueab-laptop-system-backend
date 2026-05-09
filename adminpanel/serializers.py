from rest_framework import serializers
from laptops.models import Laptop
from users.models import User
from transactions.models import Transaction

class AdminOverviewSerializer(serializers.Serializer):

    total_laptops = serializers.IntegerField()
    laptops_inside = serializers.IntegerField()
    laptops_outside = serializers.IntegerField()

    total_students = serializers.IntegerField()
    total_security = serializers.IntegerField()
    total_admins = serializers.IntegerField()

    total_transactions = serializers.IntegerField()
    today_transactions = serializers.IntegerField()


class UserMiniSerializer(serializers.ModelSerializer):

    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "student_id",
            "role",
            "profile_photo"
        ]

    def get_profile_photo(self, obj):

        request = self.context.get("request")

        if obj.profile_photo:
            return request.build_absolute_uri(
                obj.profile_photo.url
            )

        return None


class AdminLaptopSerializer(serializers.ModelSerializer):

    owner = UserMiniSerializer()
    current_holder = UserMiniSerializer()

    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Laptop

        fields = [
            "id",
            "brand",
            "serial_number",
            "owner",
            "current_holder",
            "is_inside_library",
            "is_checked_out",
            "qr_code",
            "created_at",
            "updated_at",
        ]

    def get_qr_code(self, obj):

        request = self.context.get("request")

        if obj.qr_code:
            return request.build_absolute_uri(
                obj.qr_code.url
            )

        return None
    
class AdminUserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()
    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "student_id",
            "role",
            "profile_photo",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_profile_photo(self, obj):

        request = self.context.get("request")

        if obj.profile_photo:
            return request.build_absolute_uri(
                obj.profile_photo.url
            )

        return None
    
class AdminTransactionSerializer(serializers.ModelSerializer):

    laptop = AdminLaptopSerializer()
    student = UserMiniSerializer()
    previous_holder = UserMiniSerializer()
    new_holder = UserMiniSerializer()
    scanned_by = UserMiniSerializer()

    class Meta:
        model = Transaction

        fields = [
            "id",
            "laptop",
            "student",
            "previous_holder",
            "new_holder",
            "scanned_by",
            "action_type",
            "created_at",
            "updated_at",
        ]