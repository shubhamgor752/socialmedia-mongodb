from django.db import models
from administartion.models import UserProfile, CustomUser


# Create your models here.


class Post(models.Model):
    post_title = models.CharField(max_length=65)
    author = models.ForeignKey(UserProfile , on_delete = models.CASCADE , related_name = 'create_post')
    likes = models.ManyToManyField(UserProfile , related_name='like_post', blank=True)
    description = models.TextField()