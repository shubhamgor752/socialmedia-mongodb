from django.urls import path
from .views import SignInViewset , UserViewset , SwitchAccountViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("signin", SignInViewset, basename="signin")

router.register("user/update", UserViewset, basename="user_update")

router.register("switch/acc", SwitchAccountViewSet, basename="switch_account")


urlpatterns = router.urls