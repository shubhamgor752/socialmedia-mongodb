from django.db import models
from administartion.models import CustomUser , UserProfile


# Create your models here.


class ChatMessage(models.Model):
    sender = models.ForeignKey(UserProfile , on_delete=models.CASCADE , related_name = 'sent_messages')
    receiver = models.ForeignKey(UserProfile , on_delete = models.CASCADE , related_name = 'received_messages')
    message = models.TextField()
    suggested_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    forwarded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='forwarded_messages', null=True, blank=True)


    class Meta:
        verbose_name = "chat system"
        verbose_name_plural = "chat systems"


    def __str__(self) -> str:
        return f"From: {self.sender} | To : {self.receiver} | Message : {self.message[:50]}......."