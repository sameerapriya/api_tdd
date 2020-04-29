from django.urls import path
from .views import UserView, AuthTokenView

app_name = 'user'

urlpatterns = [
   path('create/', UserView.as_view(), name='create'),
   path('token/', AuthTokenView.as_view(), name='token'),
]
