from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import TagApiViewSet, CastApiViewSet

router = DefaultRouter()
router.register('tags', TagApiViewSet)
router.register('casts', CastApiViewSet)

app_name = 'movie'

urlpatterns = [
    path('', include(router.urls))
]
