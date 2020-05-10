from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Cast, Movie

from .serializers import CastSerializer, TagSerializer,\
    MovieSerializer, MovieDetailSerializer


class BaseMovieAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Manages the attributes of movie in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns objects for authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Creates objects of attribute"""
        serializer.save(user=self.request.user)


class TagApiViewSet(BaseMovieAttrViewSet):
    """Manages the tags in the database"""
    queryset = Tag.objects.all()

    serializer_class = TagSerializer


class CastApiViewSet(BaseMovieAttrViewSet):
    """Manages the cast in the database"""

    queryset = Cast.objects.all()

    serializer_class = CastSerializer


class MovieApiViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns objects for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Retrieval of serializer class"""
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return self.serializer_class
