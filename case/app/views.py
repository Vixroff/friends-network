from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import FriendshipRequestInOutFilter
from .models import User, FriendshipRelation
from .serializers import (
    UserSerializer,
    FriendshipRelationSerializer,
    FriendshipAcceptSerializer,
)


class RegistrationView(generics.CreateAPIView):
    """View provides User registration."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class FriendshipRequestViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """View provides retrieve a list of friendship request objects and create friendship request."""

    filter_backends = (FriendshipRequestInOutFilter,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = FriendshipRelation.objects.filter(
            Q(user_sender=user) | Q(user_recipient=user),
            accept=None
        ).select_related('user_sender', 'user_recipient')
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return FriendshipAcceptSerializer
        return FriendshipRelationSerializer

    def perform_create(self, serializer):
        mutual_request = FriendshipRelation.objects.filter(
            user_sender=self.request.data.get('request_friendship_to_user'),
            user_recipient=self.request.user,
            accept=None,
        ).first()
        if mutual_request is None:
            serializer.save(user_sender=self.request.user)
        else:
            mutual_request.accept = True
            mutual_request.save()
            serializer.instance = mutual_request


class FriendshipViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = FriendshipRelationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = FriendshipRelation.objects.filter(
            Q(user_sender=self.request.user) | Q(user_recipient=self.request.user),
            accept=True,
        ).select_related('user_sender', 'user_recipient')
        return queryset


class GetRelationView(
    generics.GenericAPIView,
):

    queryset = FriendshipRelation.objects.all()
    serializer_class = FriendshipRelationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        relation = self.get_object()
        if relation is None:
            return Response(status=204)
        serializer = self.get_serializer(relation)
        return Response(serializer.data)

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        relation = self.queryset.filter(
            Q(user_sender=self.request.user, user_recipient=user) |
            Q(user_sender=user, user_recipient=self.request.user)
        ).first()
        return relation
