from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [IsAuthenticated]
