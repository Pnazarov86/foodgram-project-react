from django.urls import include, path
# from rest_framework import routers
# from .views import FollowViewSet


# router = routers.DefaultRouter()
# router.register(r'users', FollowViewSet, basename='subscriptions')
# router.register(
#    r'users/(?P<user_id>\d+)/subscribe',
#    FollowViewSet,
#    basename='users'
# )

urlpatterns = [
   # path('', include(router.urls)),
   path('', include('djoser.urls')),
   path('auth/', include('djoser.urls.authtoken'))
]
