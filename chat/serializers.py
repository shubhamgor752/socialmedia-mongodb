from rest_framework import serializers
from chat.models import ChatMessage



class SendMessageSerializer(serializers.Serializer):
    receiver = serializers.CharField(required=False, help_text="ID of user")
    message = serializers.CharField(required=False, help_text="Message")
    forward_id = serializers.CharField(required=False, help_text="Forword message ")
    # media = serializers.ImageField(required=False, help_text="Media attachment") # its not required right now
    schedule_time = serializers.DateTimeField(required=False)


    def validate(self, fields):
        receiver = fields.get("receiver")
        message = fields.get("message")
        # media = fields.get("media")

        if not any([receiver]):
            raise serializers.ValidationError("receiver(s) ID should be present")
        if not any([message]):
            raise serializers.ValidationError("Message, attachment or post should be present")
        return fields
        

    
class EditMessageSerialzer(serializers.Serializer):
    message_id = serializers.CharField(required=False , help_text='ID of message')
    message = serializers.CharField(required=False, help_text='New message')




class SuggestionMessageSerializer(serializers.Serializer):
    message_id = serializers.CharField(required=False, help_text="ID of message")
    receiver = serializers.CharField(required=False, help_text="Forword message ")




class MyConversationSerializer(serializers.Serializer):

    sender = serializers.SerializerMethodField(required=False)
    receiver = serializers.SerializerMethodField(required=False)
    message = serializers.SerializerMethodField(required=False)

    def get_sender(self, obj):
        try:
            return obj.sender.username
        except:
            return None

    def get_receiver(self, obj):
        try:
            return obj.receiver.username
        except:
            return None

    def get_message(self, obj):
        try:
            return obj.message
        except:
            return None