from rest_framework import serializers
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
)

from .models import UserProfile
from rest_framework.response import Response


USERNAME_VALIDATORS = [
    MinLengthValidator(4,"Username must be at least 4 characters long"),
    MaxLengthValidator(50,"Username cannot be longer than 50 characters"),
    RegexValidator(
        r"^\w+$",
        message="Username can only contain letters, numbers, and underscores",
    ),
]



class UserSignUpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True)
    otp = serializers.CharField(required=False)


    @staticmethod
    def validate_phone_number(mobile_number):
        if len(str(mobile_number)) != 10:
            raise serializers.ValidationError("Length of phone number should be 10 digits")
        
        return mobile_number