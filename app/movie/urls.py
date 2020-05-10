from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import TagApiViewSet, CastApiViewSet, MovieApiViewSet

router = DefaultRouter()
router.register('tags', TagApiViewSet)
router.register('casts', CastApiViewSet)
router.register('movies', MovieApiViewSet)

app_name = 'movie'

urlpatterns = [
    path('', include(router.urls))
]
