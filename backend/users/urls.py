from django.urls import include, path
from .views import FollowViewSet

urlpatterns = [
   path('users/<str:pk>/subscribe/', FollowViewSet),
   path('', include('djoser.urls')),
   path('auth/', include('djoser.urls.authtoken'))
]
