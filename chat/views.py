from django.shortcuts import render
from rest_framework import viewsets , status , serializers
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser , IsAuthenticated
from django.http import HttpResponse
from chat.serializers import SendMessageSerializer , EditMessageSerialzer , MyConversationSerializer , SuggestionMessageSerializer
from administartion.models import UserProfile
import random
from django.db.models import Q
from datetime import datetime , timedelta
from chat.models import ChatMessage

# Create your views here.


class SendMessageViewSet(viewsets.ViewSet):
    serializer_class = SendMessageSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            request_data = serializer.validated_data
            receiver_id = request_data.get("receiver")
            message = request_data.get("message")
            forward_id = request_data.get("forward_id")

            # print(str(receiver_id) == str(request.user.id))
            if not receiver_id:
                raise serializers.ValidationError("Receiver ID should be present")
            
            if not message:
                raise serializers.ValidationError("Message should be present")
            
            if str(receiver_id) == str(request.user.id):
                return Response({"status": False, "message": "You can't send message your self"}, status=status.HTTP_403_FORBIDDEN)

            
            if forward_id:
                try:
                    forwarded_message = ChatMessage.objects.get(id=forward_id)
                except ChatMessage.DoesNotExist:
                    raise serializers.ValidationError("Forwarded message does not exist")

                message_response = ChatMessage.objects.create(
                    sender=request.user.userprofile,  
                    receiver_id=receiver_id,
                    message=forwarded_message.message,  
                    forwarded_by=request.user.userprofile  
                )
                return Response(
                    {"status": True, "message": "Message forwarded successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            else:
                # pass
                message_response = ChatMessage.objects.create(
                    sender=request.user.userprofile,  
                    receiver_id=receiver_id,
                    message=message,
                    # media=media
                )
                return Response(
                    {"status": True, "message": "Message sent successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
        else:
            return Response(
                {"status": False, "message": serializer.errors, "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
    def list(self, request , *args , **kwargs):
        try:
            receiver_profile = request.user.userprofile
            unread_msg = ChatMessage.objects.filter(receiver=receiver_profile)

            if not unread_msg:
                return Response({"message":"No Pedning message right now"})
            unread_msg.update(is_read=True)

            conversation_messages = ChatMessage.objects.filter(Q(receiver=request.user.userprofile))

            if not conversation_messages:
                return Response(
                    {
                        "status": True,
                        "message": "No conversation with any user",
                    },
                    status=status.HTTP_200_OK,
                )
            
            serializer = MyConversationSerializer(conversation_messages, many=True)

            return Response({
                "status":True , "message":"Message found successfully", "data":serializer.data
            },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
