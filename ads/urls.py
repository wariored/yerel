from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'ads'
urlpatterns = [
    path('categories/categories/', views.categories, name='categories'),
    path('create_post/', views.create_post, name='create_post'),
    path('create_post_verification/', views.create_post_verification, name='create_post_verification'),
    path('single_item/<str:random_url>', views.single_item, name='single_item'),
    path('single_item_update/<random_url>', views.single_item_update, name='single_item_update'),
    path('single_item_delete/<str:random_url>', views.single_item_delete, name='single_item_delete'),
    path('categories/categories_grid/', views.categories_grid, name='categories_grid'),
    path('single_item/like/' , views.like_ad , name="like_post")  ,

]