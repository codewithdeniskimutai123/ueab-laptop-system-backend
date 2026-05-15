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

from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    laptop_serial = serializers.SerializerMethodField()
    laptop_brand = serializers.SerializerMethodField() 
    scanned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id", "laptop", "student", "previous_holder", "new_holder", "scanned_by",
            "action_type", "created_at", "updated_at",
            "sender_name", "receiver_name", "laptop_serial",
            "laptop_brand", "scanned_by_name" 
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_sender_name(self, obj):
        if obj.previous_holder:
            return f"{obj.previous_holder.first_name} {obj.previous_holder.last_name}".strip() or obj.previous_holder.username
        return "System"

    def get_receiver_name(self, obj):
        if obj.new_holder:
            return f"{obj.new_holder.first_name} {obj.new_holder.last_name}".strip() or obj.new_holder.username
        return "System"

    def get_laptop_serial(self, obj):
        return obj.laptop.serial_number if obj.laptop else "N/A"

    def get_laptop_brand(self, obj):
        return obj.laptop.brand if obj.laptop else "Device"

    def get_scanned_by_name(self, obj):
        if obj.scanned_by:
            return f"{obj.scanned_by.first_name} {obj.scanned_by.last_name}".strip() or obj.scanned_by.username
        return "System Admin"


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
    


