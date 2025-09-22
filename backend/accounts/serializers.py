from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "role",
            "is_active",
            "permissions",
            "last_login",
            "date_joined",
        ]
        read_only_fields = ["id", "is_active", "permissions", "last_login", "date_joined"]

    def get_permissions(self, obj: User) -> dict[str, bool]:
        return obj.permissions


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(request=self.context.get("request"), username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials", code="authorization")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled", code="authorization")
        else:
            raise serializers.ValidationError("Username and password are required", code="authorization")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        token = RefreshToken(attrs["refresh"])
        data = {
            "access": str(token.access_token),
            "refresh": str(token),
        }
        return data
