from django.urls import path
from .views import SignInViewset

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("signin", SignInViewset, basename="signin")

urlpatterns = router.urls