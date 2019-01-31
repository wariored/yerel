from django.urls import path
from . import views

app_name = 'pricing'
urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('activation/<str:account_type>/', views.pricing_activation, name='activation'),
    path('activation/<str:account_type>/<str:token>/', views.pricing_activation, name='activation'),
    path('activation_verification_1/<str:account_type>/', views.pricing_activation_verification_1,
         name='activation_verification_1'),
    path('activation_verification_1/<str:account_type>/<str:token>/', views.pricing_activation_verification_1,
         name='activation_verification_1'),
    path('activation_verification_2/<str:account_type>/<str:token>/', views.pricing_activation_verification_2,
         name='activation_verification_2'),
]
# PSR-test_8Odlpj
