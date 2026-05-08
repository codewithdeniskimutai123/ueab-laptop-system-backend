from rest_framework import serializers
from .models import Laptop

class LaptopSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Laptop
        fields = [
            'id',
            'owner',
            'current_holder',
            'brand',
            'serial_number',
            'qr_code',
            'qr_code_url',
            'is_checked_out',
            'created_at'
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