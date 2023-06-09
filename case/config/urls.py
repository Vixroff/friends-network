from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
   openapi.Info(
      title="Тестовое задание ВКонтакте",
      default_version='v1',
      description="Дружеская социальная сеть",
      contact=openapi.Contact(email="maxvihr@yandex.ru"),
   ),
   public=True,
   permission_classes=[AllowAny],
)


urlpatterns = [
    path('api/', include('api.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
