from django.urls import path
from user import views

urlpatterns = [
    path('sign-up/', views.UserCreationAPIView.as_view(), name='sign_up'),
    path('sign-in/', views.RestAuthAPIView.as_view(), name='sign_in'),
]
