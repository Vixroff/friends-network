from app.models import FriendshipRelation, User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .filters import FriendshipRequestFilter
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

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FriendshipRequestFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = FriendshipRelation.objects.filter(
            Q(user_sender=self.request.user) | Q(user_recipient=self.request.user),
            is_accepted=None,
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
            is_accepted=None,
        ).first()
        if mutual_request:
            mutual_request.is_accepted = True
            mutual_request.save()
            serializer.instance = mutual_request
        else:
            serializer.save(user_sender=self.request.user)


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
            is_accepted=True,
        ).select_related('user_sender', 'user_recipient')
        return queryset


class GetRelationView(
    generics.RetrieveAPIView,
):
    """
    Check relation with user by username as URL path parameter.
    """

    queryset = FriendshipRelation.objects.all()
    serializer_class = FriendshipRelationSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        relation = self.queryset.filter(
            Q(user_sender=self.request.user, user_recipient=user) |
            Q(user_sender=user, user_recipient=self.request.user)
        ).first()
        if relation:
            return relation
        raise Http404
