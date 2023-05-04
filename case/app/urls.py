from django.urls import path, include

from .views import RegistrationView


urlpatterns = [
    path('v1/auth/', include([
        path('registration/', RegistrationView.as_view(), name='registration'),
    ])),
]
