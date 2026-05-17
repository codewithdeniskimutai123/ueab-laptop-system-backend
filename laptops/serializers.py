from rest_framework import serializers
from .models import Laptop

class LaptopSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Laptop
        fields = [
            'id', 'owner', 'current_holder', 'brand', 
            'serial_number', 'qr_code', 'qr_code_url', 
            'is_checked_out', 'created_at'
        ]
        read_only_fields = ['qr_code', 'qr_code_url', 'created_at']

    def create(self, validated_data):
        if 'current_holder' not in validated_data:
            validated_data['current_holder'] = validated_data['owner']
        return Laptop.objects.create(**validated_data)
    
    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None


class MyLaptopSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    current_holder_name = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()

    owner_id = serializers.IntegerField(
        source="owner.id",
        read_only=True
    )

    current_holder_id = serializers.IntegerField(
        source="current_holder.id",
        read_only=True
    )

    class Meta:
        model = Laptop
        fields = [
            "id",
            "brand",
            "serial_number",
            "is_inside_library",
            "owner_id",
            "current_holder_id",
            "owner_name",
            "current_holder_name",
            "qr_code",
            "qr_code_url",
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    def get_current_holder_name(self, obj):
        if obj.current_holder:
            return f"{obj.current_holder.first_name} {obj.current_holder.last_name}"
        return None

    def get_qr_code_url(self, obj):
        request = self.context.get("request")

        if obj.qr_code and request:
            return request.build_absolute_uri(
                obj.qr_code.url
            )

        elif obj.qr_code:
            return obj.qr_code.url

        return None