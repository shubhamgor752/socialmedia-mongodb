from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from .serializers import createpostserializer , LikePostSerializer,LikeViewSerializer , ListpostSerializer
from administartion.models import UserProfile , CustomUser
from django.db.models import Q , Sum
from django.utils.crypto import get_random_string
from  django.utils import timezone
from .models import Post
from rest_framework.parsers import MultiPartParser, FormParser
from openai.error import RateLimitError
import os
from dotenv import load_dotenv
from custom_pagination import CustomPagination
import openai
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')


# Create your views here.


class CreatePostViewSet(viewsets.ViewSet, CustomPagination):
    parser_classes = (MultiPartParser, FormParser)  # <- CRUCIAL
    permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination

    def create(self, request):
        print("DEBUG request.data:", request.data) 
        print("DEBUG request.FILES:", request.FILES)
        serializer = createpostserializer(data=request.data)


        if serializer.is_valid():
            post_title = serializer.validated_data.get("post_title")
            description = serializer.validated_data.get("description")

            image = serializer.validated_data.get("image")  # Changed from `image`
            print("image-------------" , image)
            author = request.user.userprofile

            post = Post.objects.create(
                post_title=post_title,
                author=author,
                image=image
            )

            image_url = post.image.url  # <- Cloudinary URL

            print("image_url------" , image_url)

            # Generate description using OpenAI
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a creative AI that writes social media captions."},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Write a fun caption for this image."},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]}
                    ],
                    max_tokens=100
                )
        
                print("response---------" , response)

                description = response.choices[0].message["content"].strip()
                post.description = description
                post.save()

                return Response({
                    "status": True,
                    "message": "Post created successfully with AI caption.",
                    "data": {
                        "post_id": post.id,
                        "post_title": post.post_title,
                        "description": post.description,
                        "image_url": post.image.url
                    }
                })

            except RateLimitError:

                description = description
                post.description = description
                post.save()

                return Response({
                    "status": True,
                    "message": "Post created successfully with AI caption.",
                    "data": {
                        "post_id": post.id,
                        "post_title": post.post_title,
                        "description": post.description,
                        "image_url": post.image.url
                    }
                })
        return Response(
            {"status": False, "message": serializer.errors, "data": {}},
            status=status.HTTP_400_BAD_REQUEST
        )

    def list(self,request):
        try:
            queryset = Post.objects.filter(author=request.user)
            results = self.paginate_queryset(queryset, request, view=self)
            serializer = ListpostSerializer(results,many=True)
            self.message = 'Post fetched successfully'
            self.res_status = True
            self.data = serializer.data
            self.count = queryset.count()

            return Response({'data': self.data,
                            'message': self.message,
                            'res_status': self.res_status,
                            'code': HttpResponse.status_code})

        except Exception as e:
            return Response(
                {"status": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )