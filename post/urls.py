from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreatPostViewSet

router = DefaultRouter()

router.register("create/post", CreatPostViewSet , basename='create_post')



urlpatterns = []

urlpatterns += router.urls