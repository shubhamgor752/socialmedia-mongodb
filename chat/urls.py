from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SendMessageViewSet,EditMessageViewSet, SuggestMessageViewSet , conversationViewSet ,PendingMsgViewSet

router = DefaultRouter()

urlpatterns = [

]

router.register("message/send", SendMessageViewSet, basename="send_message")

router.register("edit/message",EditMessageViewSet , basename="edit_msg")

router.register("message/suggest",SuggestMessageViewSet,basename='suggest_message')

router.register("my/con", conversationViewSet , basename='my_con')

router.register("pending/mesg", PendingMsgViewSet , basename='pending_mesg')



urlpatterns += router.urls
