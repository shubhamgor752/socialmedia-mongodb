from django.shortcuts import render
from connection.models import Connection
from rest_framework import viewsets , status
from rest_framework.permissions import AllowAny , IsAdminUser , IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from administartion.models import UserProfile
from connection.serializers import FolloweSerializer
from rest_framework.response import Response
# Create your views here.


class FollowRequestViewSet(viewsets.ViewSet):
    serializer_class = FolloweSerializer
    permission_classes = (IsAuthenticated,)


    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                followers_username = data.get('followers')

                if followers_username:
                    first_follower = followers_username[0]  # Get the first follower
                    username = first_follower.username  # Assuming 'username' is the attribute holding the username


                follower = UserProfile.objects.filter(username=username) # check if user in db

                if not follower:
                    return Response({
                        "status":False,
                        "message":"User Not Found"
                    })

                user = request.user.userprofile

                if user.username == follower.username:
                    return Response(
                            {"status": False, "message": "You can't follow yourself"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                

                if Connection.objects.filter(user=user , follower=follower).exists():
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
                    {"status": False, "message": serializer.errors, "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            print(e)
            return Response(
                {"status": False, "message": "An error occurred", "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )