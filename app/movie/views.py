from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Cast, Movie

from .serializers import CastSerializer, TagSerializer,\
    MovieSerializer, MovieDetailSerializer, MovieImageSerializer
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser


class BaseMovieAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Manages the attributes of movie in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns objects for authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(movie__isnull=False)
        return queryset.filter(
            user=self.request.user).order_by('-name').distinct()

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
    parser_classes = (FormParser, MultiPartParser, JSONParser)

    def _params_to_int(self, qs):
        """Returns a string format of id to a list format"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Returns objects for authenticated user"""
        tag = self.request.query_params.get('tag')
        cast = self.request.query_params.get('cast')
        queryset = self.queryset
        if tag:
            tag_ids = self._params_to_int(tag)
            queryset = queryset.filter(tag__id__in=tag_ids)
        if cast:
            cast_ids = self._params_to_int(cast)
            queryset = queryset.filter(cast__id__in=cast_ids)

        return queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Retrieval of serializer class"""
        if self.action == 'retrieve':
            return MovieDetailSerializer
        elif self.action == 'upload_image':
            return MovieImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a movie"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uploads an image to a movie"""
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
