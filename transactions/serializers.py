from rest_framework import serializers
from .models import Transaction
from laptops.models import Laptop
from users.models import User


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
            "profile_photo"
        ]

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if obj.profile_photo and request:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None

class LaptopMiniSerializer(serializers.ModelSerializer):

    owner = UserMiniSerializer()
    current_holder = UserMiniSerializer()

    class Meta:
        model = Laptop
        fields = [
            "id",
            "brand",
            "serial_number",
            "owner",
            "current_holder",
        ]
class TransactionSerializer(serializers.ModelSerializer):

    laptop = LaptopMiniSerializer()
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

        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class StudentTransactionSerializer(serializers.ModelSerializer):

    laptop_brand = serializers.CharField(source="laptop.brand", read_only=True)
    laptop_serial = serializers.CharField(source="laptop.serial_number", read_only=True)

    scanned_by_name = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = [
            "id",
            "laptop_brand",
            "laptop_serial",
            "action_type",
            "created_at",
            "scanned_by_name",
        ]

    def get_scanned_by_name(self, obj):
        if obj.scanned_by:
            return f"{obj.scanned_by.first_name} {obj.scanned_by.last_name}"
        return None
    

class SecurityTransactionSerializer(serializers.ModelSerializer):

    laptop_brand = serializers.CharField(source="laptop.brand", read_only=True)
    laptop_serial = serializers.CharField(source="laptop.serial_number", read_only=True)

    scanned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "laptop_brand",
            "laptop_serial",
            "action_type",
            "created_at",
            "scanned_by_name",
        ]

    def get_scanned_by_name(self, obj):
        if obj.scanned_by:
            return f"{obj.scanned_by.first_name} {obj.scanned_by.last_name}"
        return None