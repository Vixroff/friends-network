from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny


from .models import User, FriendshipRelation
from .serializers import UserSerializer, FriendshipSerializer


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=(AllowAny,)


class FriendshipRelationView(
    generics.ListAPIView,
    generics.CreateAPIView,
):
    filter_backends = (SearchFilter,)
    search_fields = ('=user_sender__username', '=user_reciever__username')
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        queryset = FriendshipRelation.objects.filter(
            Q(user_sender=self.request.user)|Q(user_reciever=self.request.user),
            accept=None
        ).select_related('user_sender', 'user_reciever')
        return queryset
    
    def perform_create(self, serializer):
        try:
            mutual_request = FriendshipRelation.objects.get(
                user_sender=self.request.data.get('user_reciever'),
                user_reciever=self.request.user
            )
        except FriendshipRelation.DoesNotExist:
            serializer.save(user_sender=self.request.user)
        else:
            mutual_request.delete()
            serializer.save(user_sender=self.request.user, accept=True)
