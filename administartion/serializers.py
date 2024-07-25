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
    


class UserProfileInfo(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        
        fields = (
            "id",
            "bio",
            "first_name",
            "email",
            "phone_number",
            "profession",
            "username",
            "profile_picture"
        )


class CustomUserSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    username = serializers.CharField(validators=USERNAME_VALIDATORS)
    first_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(
        required=True,
    )
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    date_of_birth = serializers.DateField(required=False)
    profession = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False)

    # def update(self, instance, validated_data):
    #     # Update the instance with the validated data
    #     instance.username = validated_data.get('username', instance.username)
    #     instance.first_name = validated_data.get("first_name", instance.first_name)
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.bio = validated_data.get('bio',instance.bio)
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.save()
    #     return instance

    def update(self, instance, validated_data):
        # response = {}

        # Update context with validated data or default to instance attributes
        context = {
            "id": str(instance.id),
            "username": validated_data.get("username", instance.username),
            "first_name": validated_data.get("first_name", instance.first_name),
            "bio": validated_data.get("bio", instance.bio),
            "email": validated_data.get("email", instance.email),
            # "phone_number": validated_data.get("phone_number", instance.phone_number)
        }

        # Get the instance if it's not None
        if instance:
            instance = UserProfile.objects.filter(id=instance.id).first()
            context["phone_number"] = validated_data.get(
                "phone_number", instance.phone_number
            )
            context["date_of_birth"] = validated_data.get(
                "date_of_birth", instance.date_of_birth
            )
            context["profession"] = validated_data.get(
                "profession", instance.profession
            )
            context["bio"] = validated_data.get(
                "bio",instance.bio
            )
            context["profile_picture"] = validated_data.get("profile_picture",instance.profile_picture)


            serializer_class = UserProfileInfo

            for key, value in context.items():
                setattr(instance, key, value)
            instance.save()
            response = serializer_class(instance).data

            # print(response)

            return instance

        

