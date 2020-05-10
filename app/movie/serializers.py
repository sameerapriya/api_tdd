from rest_framework import serializers

from core.models import Tag, Cast, Movie


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag Model"""
    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class CastSerializer(serializers.ModelSerializer):
    """Serializer for cast objects"""
    class Meta:
        model = Cast
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for movie objects"""
    cast = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Cast.objects.all())
    tag = serializers.PrimaryKeyRelatedField(many=True,
                                             queryset=Tag.objects.all())

    class Meta:
        model = Movie
        fields = ('id', 'title', 'url', 'tag', 'cast', 'duration', 'price')
        read_only_fields = ('id',)
