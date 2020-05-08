from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import TagApiViewSet

router = DefaultRouter()
router.register('tags', TagApiViewSet)

app_name = 'movie'

urlpatterns = [
    path('', include(router.urls))
]
