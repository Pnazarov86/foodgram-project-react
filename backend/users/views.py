from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from api.serializers import FollowSerializer
from .serializers import CustomUserSerializer
from .models import Follow, User
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.decorators import action


class FollowListViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет списка подписчиков."""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class CustomUserViewSet(UserViewSet):
    """Вьюсет пользователей."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Follow,
                user=user,
                author=author)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
