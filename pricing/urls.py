from django.urls import path
from . import views

app_name = 'pricing'
urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('activation/<str:account_type>/', views.pricing_activation, name='activation'),
]
