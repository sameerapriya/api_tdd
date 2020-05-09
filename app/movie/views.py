from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Cast

from .serializers import TagSerializer, CastSerializer


class TagApiViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    """Manages the tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()

    serializer_class = TagSerializer

    def get_queryset(self):
        """Return objects for the authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Allows to create tags"""
        serializer.save(user=self.request.user)


class CastApiViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manages the cast in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Cast.objects.all()

    serializer_class = CastSerializer

    def get_queryset(self):
        """Returns cast for authenticated users only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
