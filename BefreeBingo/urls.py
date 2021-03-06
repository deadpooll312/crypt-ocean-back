"""BefreeBingo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.views import logout_then_login
from user.views import TrackUserTrafficAPIView, CommonSettingsAPIView, \
    UserTrafficTrackerListView, LoginView, RegisterUserClickAPIView, UserClickTrackerListView

from BefreeBingo import settings

schema_view = get_schema_view(
    openapi.Info(
        title="BefreeBingo API",
        default_version='v1',
        description="API Documentation",
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    # permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('jet', include('jet.urls')),
    path('admin/', admin.site.urls),

    path('api/', include([
        path('v1/', include([
            path('auth/', include(('user.urls', 'user'))),
            path('bets/', include(('bets.urls', 'bets'))),

            path('traffic/track/', TrackUserTrafficAPIView.as_view(), name='traffic_tracker'),
            path('traffic/click/track/', RegisterUserClickAPIView.as_view(), name='click_tracker'),
            path('common/settings/', CommonSettingsAPIView.as_view(), name='common_settings')
        ])),
    ])),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_then_login, name='logout'),
    path('', UserTrafficTrackerListView.as_view(), name='index'),
    path('clicks/', UserClickTrackerListView.as_view(), name='user_clicks')
]

if settings.DEBUG:
    urlpatterns += [
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
    ]
