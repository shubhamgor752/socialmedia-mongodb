from rest_framework.routers import DefaultRouter
from connection.views import (
    FollowRequestView,
    AcceptFollowRequestView,
    FollowbackView,
    MyfollowerListView,
    MyFollowingListView,
)
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path("acceptfollowrequest", AcceptFollowRequestView.as_view())

]

router.register("follow/send", FollowRequestView, basename="send_follow")
router.register("follow/back", FollowbackView, basename="followback")

router.register("followers/list", MyfollowerListView , basename="follower_list")

router.register("following/list", MyFollowingListView , basename="following_list")


urlpatterns += router.urls
