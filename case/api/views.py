from http import HTTPStatus

from app.models import FriendshipRelation, User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import FriendshipRequestInOutFilter
from .serializers import (FriendshipAcceptSerializer,
                          FriendshipRelationSerializer, UserSerializer)


class RegistrationView(generics.CreateAPIView):
    """
    User registration capability.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class FriendshipRequestViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Handling of a friendship requests. Create new one, get all, accept/reject incoming.
    """

    filter_backends = (FriendshipRequestInOutFilter,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = FriendshipRelation.objects.filter(
            Q(user_sender=user) | Q(user_recipient=user),
            accept_is=None,
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
            accept_is=None,
        ).first()
        if mutual_request is None:
            serializer.save(user_sender=self.request.user)
        else:
            mutual_request.accept_is = True
            mutual_request.save()
            serializer.instance = mutual_request


class FriendshipViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Handling of a accepted friendships. Get all, delete one."""

    serializer_class = FriendshipRelationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = FriendshipRelation.objects.filter(
            Q(user_sender=self.request.user) | Q(user_recipient=self.request.user),
            accept_is=True,
        ).select_related('user_sender', 'user_recipient')
        return queryset


class GetRelationView(
    generics.GenericAPIView,
):
    """
    Check relation with user by username as URL path parameter.
    """

    queryset = FriendshipRelation.objects.all()
    serializer_class = FriendshipRelationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        relation = self.get_object()
        if relation is None:
            return Response(status=HTTPStatus.NO_CONTENT)
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
