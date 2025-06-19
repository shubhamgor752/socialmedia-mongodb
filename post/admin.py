from django.contrib import admin
from .models import Post

# Register your models here.


class postadmin(admin.ModelAdmin):
    fields = ["author", "post_title","likes","description", "image"]
    list_display = ["id", "author", "post_title",  "description","image","get_like_display"]

    def get_like_display(self,obj):
        return ", ".join(like.username for like in obj.likes.all())

    get_like_display.short_description = 'Likes'

admin.site.register(Post,postadmin)