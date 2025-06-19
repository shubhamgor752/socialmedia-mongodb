from rest_framework import serializers
from post.models import Post


class createpostserializer(serializers.Serializer):
    post_title = serializers.CharField()
    description = serializers.CharField()
    image = serializers.ImageField(required=True)  



    def update(self, instance, validated_data):

        instance.post_title = validated_data.get("post_title" , instance.post_title)
        instance.description = validated_data.get("description", instance.description)
        instance.image = validated_data.get("image" , instance.image)


class LikePostSerializer(serializers.Serializer):
    post_id = serializers.CharField()



class LikeViewSerializer(serializers.Serializer):
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return [user.username for user in obj.likes.all()]
    

class ListpostSerializer(serializers.ModelSerializer):
    # comments = CreateCommentSerializer(many=True, read_only=True)
    likes = LikeViewSerializer(source='*')
    author = serializers.StringRelatedField()

    def get_comment_name(self,obj):
        return obj.author.username

    class Meta:
        model = Post
        fields = ['author','post_title', 'description','likes']