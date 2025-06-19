from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreatePostViewSet

router = DefaultRouter()

router.register("create/post", CreatePostViewSet , basename='create_post')



urlpatterns = []

urlpatterns += router.urls