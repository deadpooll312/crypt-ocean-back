from django.urls import path, include
from user import views

urlpatterns = [
    path('sign-up/', views.UserCreationAPIView.as_view(), name='sign_up'),
    path('sign-in/', views.RestAuthAPIView.as_view(), name='sign_in'),
    path('me/', views.GetProfileAPIView.as_view(), name='get_profile'),
    path('me/update/', views.UserUpdateAPIView.as_view(), name='update_profile'),
    path('transactions/', views.UserTransactionHistoryAPIView.as_view(), name='transactions'),


    path('password-recovery/', include([
        path('request/', views.RecoverPasswordAPIView.as_view(), name='recover_request'),
        path('token/check/', views.CheckRecoverTokenAPIView.as_view(), name='recover_check'),
        path('password/change/', views.ChangePasswordAPIView.as_view(), name='recover_change_password'),
    ])),


    path('balance/', include([
        path('fill/', include([
            path('', views.FillBalanceAPIView.as_view(), name='balance_fill'),

            path('success/', views.FillBalanceSuccessCallbackAPIView.as_view(), name='balance_fill_success'),
            path('failure/', views.FillBalanceFailureCallbackAPIView.as_view(), name='balance_fill_failure'),
            path('callback/', views.FillBalanceCallbackAPIView.as_view(), name='balance_fill_callback')
        ])),

        path('history/', views.UserFillHistoryAPIView.as_view(), name='balance_history'),
    ])),

    path('bets/', include([
        path('history/', views.UserBetsHistoryApiView.as_view(), name='bets_history')
    ]))
]
