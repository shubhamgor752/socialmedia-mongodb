from rest_framework import serializers
from post.models import Post


class createpostserializer(serializers.Serializer):
    post_title = serializers.CharField()
    description = serializers.CharField()


    def update(self, instance, validated_data):

        instance.post_title = validated_data.get("post_title" , instance.post_title)
        instance.description = validated_data.get("description", instance.description)