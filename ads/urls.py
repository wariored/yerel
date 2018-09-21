from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'ads'
urlpatterns = [
    path('categories/categories/', views.categories, name='categories'),
]