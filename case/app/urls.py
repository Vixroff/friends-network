from django.urls import path, include

from .views import RegistrationView, FriendshipRequestView


urlpatterns = [
    path('auth/', include([
        path('registration/', RegistrationView.as_view(), name='registration'),
    ])),
    path('requests/', FriendshipRequestView.as_view(), name='friendship-requests')
]
