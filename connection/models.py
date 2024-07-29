from django.db import models
from administartion.models import UserProfile
# Create your models here.


class Connection(models.Model):

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    followers = models.ManyToManyField(UserProfile , related_name='followers', blank=True)
    following = models.ManyToManyField(UserProfile , related_name='following', blank=True)
    pending_followers = models.ManyToManyField(UserProfile, related_name='pending_followers', blank=True)


    def __str__(self) -> str:
        return f"{self.user}"
    

    def get_followers(self):
        return self.followers.all()