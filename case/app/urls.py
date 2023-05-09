from django.urls import path, include

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    RegistrationView,
    FriendshipRequestViewSet,
    FriendshipViewSet,
    GetRelationView
)


router = SimpleRouter()
router.register('friendships', FriendshipViewSet, basename='friendships')
router.register('requests', FriendshipRequestViewSet, basename='requests')


urlpatterns = [
    path('auth/', include([
        path('registration/', RegistrationView.as_view(), name='registration'),
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    path('', include(router.urls)),
    path('relations/<str:username>/', GetRelationView.as_view(), name='relations-detail'),
]
