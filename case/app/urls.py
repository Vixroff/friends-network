from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from .views import (FriendshipRequestViewSet, FriendshipViewSet,
                    GetRelationView, RegistrationView)

router = SimpleRouter()
router.register('friendships', FriendshipViewSet, basename='friendships')
router.register('requests', FriendshipRequestViewSet, basename='requests')


auth_patterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]


urlpatterns = [
    path('v1/', include([
        path('auth/', include(auth_patterns)),
        path('', include(router.urls)),
        path('relations/<str:username>', GetRelationView.as_view(), name='relations-detail'),
    ])),
]
