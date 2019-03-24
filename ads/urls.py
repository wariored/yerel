from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'ads'
urlpatterns = [
    path('categories/categories/', views.categories, name='categories'),
    path('create_post/', views.create_post, name='create_post'),
    path('create_post_verification/', views.create_post_verification, name='create_post_verification'),
    path('single_item/<str:random_url>/', views.single_item, name='single_item'),
    path('single_item_update/<random_url>/', views.single_item_update, name='single_item_update'),
    path('single_item_delete/<str:random_url>/', views.single_item_delete, name='single_item_delete'),
    path('categories/categories_grid/', views.categories_grid, name='categories_grid'),
    path('ad/like/', views.like_ad, name="like_post"),
    path('favourite_ads/', views.favourite_ads, name="favourite_ads"),
    path('unlike/', views.unlike_ad, name="unlike"),
    path('my_ads/', views.my_ads, name="my_ads"),
    path('my_alerts/', views.my_alert_confirmation, name="my_alert_confirmation"),
    path('my_alerts/confirmation', views.my_alerts, name="my_alerts"),
    path('ad/feature/', views.feature_ad, name="feature_ad"),
    path('delete/', views.delete_ad, name="delete_ad"),
    path('delete/<str:ad_id>/', views.delete_ad, name="delete_ad"),
    path('status/', views.ad_status, name="ad_status"),
    path('update/<str:random_url>/', views.update_ad, name="update_ad"),
    path('update_ad_verification/<str:random_url>/', views.update_ad_verification, name="update_ad_verification"),
    path('signal/<random_url>', views.signal, name="signal"),
]
