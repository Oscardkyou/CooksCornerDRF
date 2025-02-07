from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import User


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=15, min_length=8, write_only=True)
    password_confirm = serializers.CharField(
        max_length=15, min_length=8, write_only=True
    )

    def validate(self, data):
        user = User.objects.filter(email=data["email"]).first()
        if user is not None:
            raise ValidationError("User with this email already exists.")
        if data["password"] != data["password_confirm"]:
            raise ValidationError("Passwords don't match")
        validate_password(data["password"])
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data.pop("username")
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=15)
    new_password = serializers.CharField(max_length=15)
    new_password_confirm = serializers.CharField(max_length=15)

    def validate(self, data):
        user = self.context["user"]
        if not user.check_password(data["old_password"]):
            raise ValidationError("Password is incorrect.")
        if data["new_password"] != data["new_password_confirm"]:
            raise ValidationError("Passwords don't match.")
        validate_password(data["new_password"])
        return data
