from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from .serializers import createpostserializer
from administartion.models import UserProfile , CustomUser
from django.db.models import Q , Sum
from django.utils.crypto import get_random_string
from  django.utils import timezone
from .models import Post


# Create your views here.


class CreatPostViewSet(viewsets.ViewSet):
    serializer_class = createpostserializer
    permission_classes = (IsAuthenticated,)

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                post_title = validated_data.get("post_title")
                description = validated_data.get("description")

                author = request.user.userprofile

                message_response = Post.objects.create(
                    author = author,
                    post_title = post_title,
                    description = description
                )
                return Response(
                            {"status": True, "message": "Post Create Successfully", "data": serializer.data},
                            status=status.HTTP_201_CREATED,
                        )
            else:
                    return Response(
                        {"status": False, "message": serializer.errors, "data": {}},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            
        except Exception as e:
            return Response(
                {"status": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
