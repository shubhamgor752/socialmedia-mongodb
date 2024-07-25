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
from django.utils import timezone
from base.message import suggested_messages

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


    def destroy(self,request,pk=None):
        try:
            message = ChatMessage.objects.getO(id=pk)
            if message.sender == request.user.userprofile:
                message.delete()
                return Response({
                    "status":True,
                    "message":"message delete succesfully",
                },
                status=status.HTTP_200_OK
                )
            else:
                return Response({"status": False, "message": "You don't have permission to delete this message"}, status=status.HTTP_403_FORBIDDEN)
            
        except ChatMessage.DoesNotExist:
            return Response({"status": False, "message": "Message not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EditMessageViewSet(viewsets.ViewSet):
    serializer_class = EditMessageSerialzer
    permission_classes = (IsAuthenticated,)

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request_data = serializer.validated_data
                message_id = request_data.get("message_id")
                message = request_data.get("message")

                if not message_id:
                    raise serializers.ValidationError("Message ID should be present")


                try:
                    message_to_edit = ChatMessage.objects.filter(id=message_id)
                except ChatMessage.DoesNotExist:
                    raise serializer.ValidationError("Message to edit does not exist")
                

                if request.user.userprofile == message_to_edit.sender:
                    time_elapsed = timezone.now() - message_to_edit.timestamp

                    if time_elapsed.total_second() <= 120:
                        message_to_edit.message = message

                        message_to_edit.save()
                        return Response(
                            {"status": True, "message": "Message edited successfully", "data": serializer.data},
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"status": False, "message": "Message can't be edited after 2 minutes"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"status": False, "message": "You are not allowed to edit this message", "data": {}},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                
            else:
                return Response(
                    {"status": False, "message": serializer.errors, "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            return Response(
                {"status": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SuggestMessageViewSet(viewsets.ViewSet):
    serializer_class = SuggestionMessageSerializer
    permission_classes = (IsAuthenticated,)

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                request_data = serializer.validated_data
                message_id = request_data.get("message_id")
                receiver = request.user.userprofile

                try:
                    sender_message = ChatMessage.objects.get(id=message_id)
                except ChatMessage.DoesNotExist:
                    return Response({"error": "Message with the given ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
                

                if sender_message.receiver == receiver:
                    if sender_message.id == int(message_id):
                        sender_message.suggested_message = suggested_messages
                        sender_message.save()

                        return Response(
                            {"status": True, "message": "Suggested message sent successfully", "data": serializer.data},
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response({"error": "Permission denied"},status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({"error": "Permission denied. You can only suggest messages where you are the receiver."},status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)