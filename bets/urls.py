from django.urls import path
from bets import views

urlpatterns = [
    path('coefficients/', views.CoefficientListAPIView.as_view(), name='coefficients'),
    path('make/bet/', views.MakeBetAPIView.as_view(), name='make_bet')
]
