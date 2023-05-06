from django.urls import path, include

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    RegistrationView,
    FriendshipRequestView,
    FriendshipAcceptView,
    FriendshipView,
)


router = SimpleRouter(trailing_slash=False)
router.register(r'friendships', FriendshipView, basename='friendships')


urlpatterns = [
    path('auth/', include([
        path('registration/', RegistrationView.as_view(), name='registration'),
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    path('requests/', FriendshipRequestView.as_view(), name='friendship_requests'),
    path('requests/<uuid:pk>', FriendshipAcceptView.as_view(), name='accept_friendship'),
    path('', include(router.urls)),
]
