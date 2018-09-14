from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^categories/$', views.CategoryList.as_view(), name='category-list'),
    url(r'^categories/(?P<pk>[0-9]+)/$', views.CategoryDetail.as_view(), name='category-by-id'),
    url(r'^categories/(?P<pk>[0-9]+)/subcategories/$', views.CategorySubcategories.as_view(), name='category-subcategories'),
    url(r'^subcategories/$', views.SubcategoryList.as_view(), name='subcategory-list'),
    url(r'^subcategories/(?P<pk>[0-9]+)/$', views.SubcategoryDetail.as_view(), name='subcategory-by-id'),
    url(r'^subcategories/(?P<pk>[0-9]+)/category/$', views.SubcategoryCategory.as_view(), name='subcategory-category'),
]
urlpatterns = format_suffix_patterns(urlpatterns)