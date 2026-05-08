from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'student_id',
            'last_name',
            'email',
            'phone_number',
            'profile_photo',
            'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'student' 
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user