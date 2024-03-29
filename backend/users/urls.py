from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet, FollowListViewSet

router = routers.DefaultRouter()
router.register(
    r'users/subscriptions',
    FollowListViewSet,
    basename='subscriptions'
)
router.register(r'users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
