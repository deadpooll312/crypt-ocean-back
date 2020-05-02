from django.urls import path
from user import views

urlpatterns = [
    path('sign-up/', views.UserCreationAPIView.as_view(), name='sign_up'),
    path('sign-in/', views.RestAuthAPIView.as_view(), name='sign_in'),
    path('me/', views.GetProfileAPIView.as_view(), name='get_profile'),

    path('balance/fill/', views.FillBalanceAPIView.as_view(), name='balance_fill'),

    path('balance/fill/success/', views.FillBalanceSuccessCallbackAPIView.as_view(), name='balance_fill_success'),
    path('balance/fill/failure/', views.FillBalanceFailureCallbackAPIView.as_view(), name='balance_fill_failure')
]
