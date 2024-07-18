from django.shortcuts import render
from .models import UserProfile , CustomUser
from rest_framework import viewsets,status
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny,IsAuthenticated
from administartion.serializers import UserSignUpSerializer,USERNAME_VALIDATORS
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from django.core.serializers import serialize
from django.core.exceptions import ValidationError

# Create your views here.


class SignInViewset(viewsets.ViewSet):
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)


    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            mobile_number = dict(serializer.validated_data)["mobile_number"]
            otp = (
                dict(serializer.validated_data)["otp"]
                if "otp" in dict(serializer.validated_data).keys()
                else None
            )

            print("otppp====", otp)

            if str(otp) and str(otp) == "1234":
                user_instance = UserProfile.objects.filter(phone_number=mobile_number).first()
                if user_instance:
                    user_token = Token.objects.filter(user=user_instance).first()
                    if not user_token:
                        user_token = Token.objects.create(user=user_instance)
                    message = "Sign-in complete. You're now connected and ready to go."
                    response = {
                        "user_token":user_token.key,
                        "mobile_number":mobile_number
                    }
                else:
                    user_instance = UserProfile.objects.create(phone_number = mobile_number , is_superuser=True)
                    if user_instance !={}:
                        user_token = Token.objects.filter(user=user_instance).first()
                        if not user_token:
                            user_token = Token.objects.create(user=user_instance)
                        response = {
                            "user_token": user_token.key,
                            "mobile_number": mobile_number,
                        }
                        message = "Great news! User creation is a success. Get ready to embark on your journey."
            else:
                return Response({"message":"Invalid otp"})
            self.res_status = True
            self.data = response
            self.message = message
            return Response(
                {"status": self.res_status, "message": self.message, "data": self.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": self.res_status,
                "code": HttpResponse.status_code,
                "message": self.message,
                # "data": self.data,
            }
        )




