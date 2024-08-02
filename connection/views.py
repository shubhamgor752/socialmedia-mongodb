from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets , status , serializers
from django.shortcuts import get_object_or_404
from .serializers import FolloweSerializer
from .models import Connection
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from administartion.models import UserProfile
from rest_framework.decorators import permission_classes


# Create your views here.


# this api for request to private account and follow for open account
class FollowRequestView(viewsets.ViewSet):
    serializer_class = FolloweSerializer
    permission_classes = (IsAuthenticated,)
    

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                followers_username = data.get('followers')  # username of the user sending the request

                if followers_username:
                    first_follower = followers_username[0]  # Get the first follower
                    username = first_follower.username  # Assuming 'username' is the attribute holding the username


                follower = UserProfile.objects.filter(username=username).first()

                if not follower:
                    return Response(
                        {"status": False, "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                
                user = request.user.userprofile
                if user.username == follower.username:
                    return Response(
                        {"status": False, "message": "You can't follow yourself"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                if Connection.objects.filter(user=user, followers=follower).first():
                     return Response(
                        {"status": False, "message": "You are already following this user"},
                        status=status.HTTP_400_BAD_REQUEST,
                        )
                
                if follower.is_private == True:
                    connection, created = Connection.objects.get_or_create(user=follower)
                    connection.pending_followers.add(user.id)  # Use set() to update the many-to-many relationship
                
                    return Response(
                        {"status": True, "message": "Follow request sent successfully"},
                        status=status.HTTP_201_CREATED,
                    )
                
                else:
                    connection, created = Connection.objects.get_or_create(user=user)
                    connection.following.add(follower)  # Use set() to update the many-to-many relationship


                    follower_connection, follower_created = Connection.objects.get_or_create(user=follower)
                    follower_connection.followers.add(user)
                    
                
                    return Response(
                        {"status": True, "message": "User Account is Open, followed successfully"},
                        status=status.HTTP_201_CREATED,
                    )
        
            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            print(e)
            return Response(
                {"status": False, "message": "An error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# this api user followback
class FollowbackView(viewsets.ViewSet):
    serializer_class = FolloweSerializer
    permission_classes = (IsAuthenticated,)


    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                followers_username = data.get('followers')  # username of the user sending the request
                
                if followers_username:
                    first_follower = followers_username[0]  # Get the first follower
                    username = first_follower.username

                    follow_id = first_follower.id


                    user = request.user.userprofile

                    # Iterate over each follower


                    if user.username == username:
                        return Response(
                            {"status": False, "message": "You can't follow yourself"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    

                    
                    if Connection.objects.filter(user=user, following=follow_id).first():
                        return Response(
                            {"status": False, "message": "You are already following this user"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
                    

                        
                    for username in followers_username:
                        first_follower = followers_username[0]  # Get the first follower
                        # username = first_follower.username
                        # print("followers====", username)
                        follow_id = first_follower.id




                        if Connection.objects.filter(followers=follow_id).first():
                            print("1111")


                            connection, created = Connection.objects.get_or_create(user=user)
                            connection.following.add(username)  # Use set() to update the many-to-many relationship


                            follower_connection, follower_created = Connection.objects.get_or_create(user=username)
                            follower_connection.followers.add(user)
                    
                            return Response(
                                {"status": False, "message": f"Folloback {username}"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        else:
                            return Response(
                                    {"status": False, "message": "Follower not found"},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                else:
                    # Username does not exist in the Followers column
                    return Response(
                        {"status": False, "message": "Username not found in Connections"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e)
            return Response(
                {"status": False, "message": "An error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@permission_classes([IsAuthenticated])
class AcceptFollowRequestView(APIView):
    def post(self, request):
        try:
            user = request.user.userprofile

            username = user.username

            private_user = UserProfile.objects.get(username=username)

            if private_user != user:
                return Response(
                    {"status": False, "message": "You are not authorized to accept follow requests for this account"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            connection, created = Connection.objects.get_or_create(user=user)
            pending_followers = connection.pending_followers.all()

            if pending_followers:
                for follower in pending_followers:
                    connection.pending_followers.remove(follower)
                    connection.followers.add(follower)
                    connection.following.add(follower)

                    # Adding the user to the follower's following list
                    follower_connection, _ = Connection.objects.get_or_create(user=follower)
                    follower_connection.following.add(user)
                    follower_connection.followers.add(user)

                return Response(
                    {"status": True, "message": "Follow request accepted successfully"},
                    status=status.HTTP_200_OK,
                )
            
            else:
                return Response(
                    {"status": False, "message": "No pending follow request from this user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except UserProfile.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(e)
            return Response(
                {"status": False, "message": "An error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyfollowerListView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            username_query = request.GET.get("followers", None)

            follower_obj = Connection.objects.filter(user=user)
            followers = []

            for connection in follower_obj:
                for follower in connection.followers.all():
                    if username_query:
                        if username_query.lower() in follower.username.lower():
                            followers.append({
                                "username": follower.username,
                            })
                    else:
                        followers.append({
                            "username": follower.username,
                        })

            return Response({
                "status": True,
                "message": "Followers list",
                "data": followers
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": False, "message": "An error occurred", "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyFollowingListView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            username_query = request.GET.get("following", None)

            following_obj = Connection.objects.filter(user=user)
            following = []

            for connection in following_obj:
                for followingg in connection.following.all():
                    if username_query:
                        if username_query.lower() in followingg.username.lower():
                            following.append({"username": followingg.username})
                    else:
                        following.append({"username": followingg.username})

            return Response(
                {"status": True, "message": "Following list", "data": following},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": "An error occurred", "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
