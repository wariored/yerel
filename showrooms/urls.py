from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'showrooms'
urlpatterns = [
    path('showrooms/', views.showrooms, name='showrooms'),
    path('registration/', views.registration, name='registration'),
]
