from rest_framework import serializers
from laptops.models import Laptop
from users.models import User

class LaptopUserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class LaptopsSerializer(serializers.ModelSerializer):
    owner = LaptopUserNestedSerializer(read_only=True)
    current_holder = LaptopUserNestedSerializer(read_only=True)

    class Meta:
        model = Laptop
        fields = [
            'id', 
            'brand', 
            'serial_number', 
            'qr_code', 
            'owner', 
            'current_holder', 
            'created_at'
        ]
