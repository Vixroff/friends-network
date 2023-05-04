from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny


from .models import User, FriendshipRequest
from .serializers import UserSerializer, FriendshipSerializer


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=(AllowAny,)


class FriendshipRequestView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('=user_sender__username', '=user_reciever__username')

    def get_queryset(self):
        queryset = FriendshipRequest.objects.filter(
            Q(user_sender=self.request.user)|Q(user_reciever=self.request.user),
            accept=None
        ).select_related('user_sender', 'user_reciever')
        return queryset
    
    def perform_create(self, serializer):
        try:
            mutual_request = FriendshipRequest.objects.get(
                user_sender=self.request.data.get('user_reciever'),
                user_reciever=self.request.user
            )
        except FriendshipRequest.DoesNotExist:
            return super().perform_create(self, serializer)
        else:
            mutual_request.delete()
            serializer.save(accept=True)
