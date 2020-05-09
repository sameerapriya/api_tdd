from rest_framework import serializers

from core.models import Tag, Cast


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
