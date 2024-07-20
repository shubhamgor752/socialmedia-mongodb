from django.shortcuts import render
from .models import UserProfile , CustomUser
from rest_framework import viewsets,status
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny,IsAuthenticated
from administartion.serializers import UserSignUpSerializer,USERNAME_VALIDATORS,UserProfileInfo, CustomUserSerializer
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
            if str(otp) and str(otp) == "1234":
                user_instance = UserProfile.objects.filter(phone_number=mobile_number).first()
                if user_instance:
                    user_token = Token.objects.filter(user=user_instance).first()
                    if not user_token:
                        user_token = Token.objects.create(user=user_instance)
                    message = "Sign-in complete. You're now connected and ready to go."
                    response = {
                        "user_token":user_token.key,
                        # "mobile_number":mobile_number,
                        "user": UserProfileInfo(user_instance).data,

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




class UserViewset(viewsets.ViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
    )


    def create(self, request):
        try:

            instance = get_object_or_404(CustomUser, id=request.user.id)
            serializer = self.serializer_class(
                instance, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            username = validated_data["username"].replace(" ", "_").lower()
            validated_data["username"] = username
            phone_number = validated_data.get("phone_number")
            email = validated_data.get("email")
            if (
                username
                and UserProfile.objects.filter(username=username)
                .exclude(id=instance.id)
                .exists()
            ):
                message = "Username duplicate"
            elif (
                phone_number
                and UserProfile.objects.filter(phone_number=phone_number)
                .exclude(id=instance.id)
                .exclude(is_superuser=True)
                .exists()
            ):
                message = "phone number is already in use"
            

            elif email and UserProfile.objects.filter(email=email).exclude(id=instance.id):
                message = "thiss email use already"

            else:
                response = serializer.save(request=request)
                serialized_data = self.serializer_class(response).data
                message = "User update successful"

                return JsonResponse(
                    {"status": True, "message": message, "data": serialized_data},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            # print("this waysss")
            # print("aaa excepttttt")
            message = str(e)

        return JsonResponse(
            {"status": False, "message": message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )
            

    def retrieve(self, request , pk:str = None):
        try:
            user_obj = get_object_or_404(UserProfile , id = request.user.id)
            response = UserProfileInfo(user_obj , context={"request":request}).data
            message = "User Information"
            return Response(
                {"status": True, "message": message, "data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = str(e)
        return Response(
            {"status": False, "message": message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SwitchAccountViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    message = "INVALID REQUEST"


    def create(self,request):
        try:
            user_instance = get_object_or_404(CustomUser , username = request.user.username)

            if user_instance.is_private:
                message = "Switched to public"
                user_instance.is_private = False
            else:
                message = "Switched to private"
                user_instance.is_private = True

            user_instance.save()
            return Response({
                "status":True,
                "message":message
            },
            status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            self.message = str(e)

            return Response(
            {"status": False, "message": self.message},
            status=status.HTTP_400_BAD_REQUEST,
        )