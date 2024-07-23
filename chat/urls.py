from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SendMessageViewSet

router = DefaultRouter()

urlpatterns = [

]

router.register("message/send", SendMessageViewSet, basename="send_message")

urlpatterns += router.urls
