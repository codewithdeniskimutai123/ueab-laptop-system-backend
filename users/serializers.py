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
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "student_id",
            "phone_number",
            "username",
            "role",
            "profile_photo",
        ]


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data["role"] = self.user.role
        data["username"] = self.user.username
        data["email"] = self.user.email

        return data
    
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "student_id",
            "email",
            "phone_number",
            "profile_photo",
        ]

    def update(self, instance, validated_data):

        request = self.context.get("request")

        if (
            instance.role == "student"
            and "profile_photo" in validated_data
        ):
            validated_data.pop("profile_photo")

        return super().update(
            instance,
            validated_data
        )