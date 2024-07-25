from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SendMessageViewSet,EditMessageViewSet, SuggestMessageViewSet

router = DefaultRouter()

urlpatterns = [

]

router.register("message/send", SendMessageViewSet, basename="send_message")

router.register("edit/message",EditMessageViewSet , basename="edit_msg")

router.register("message/suggest",SuggestMessageViewSet,basename='suggest_message')



urlpatterns += router.urls
