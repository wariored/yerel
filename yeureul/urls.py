"""yeureul URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth.models import User
from . import views
from django.conf import settings as conf_settings
from django.conf.urls.static import static

handler404 = 'yeureul.views.handler404'
handler500 = 'yeureul.views.handler404'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
                  path('admin/', admin.site.urls),
                  url(r'^(?P<filename>(robots.txt)|(humans.txt))$', views.home_files, name='home_files'),
                  url(r'^$', views.index, name='index'),
                  url(r'^login/$', views.login_view, name='login'),
                  url(r'^signup/$', views.signup_view, name='signup'),
                  url(r'^signup_verification/$', views.signup_verification, name='signup_verification'),
                  path('account/validate/<str:uidb64>/<str:token>/',
                       views.account_validation, name='user_activation_link'),
                  path('account/reset_password/<str:uidb64>/<str:token>/',
                       views.account_reset_password, name='user_reset_password_link'),
                  url(r'^logout/$', views.logout_view, name='logout'),
                  url(r'^contact/$', views.contact, name='contact'),
                  url(r'^contact_verification/$', views.contact_verification, name='contact_verification'),
                  url(r'^account/settings/$', views.settings, name='settings'),
                  url(r'^account/settings/update_profile/$', views.update_profile, name='update_profile'),
                  url(r'^account/settings/close_account/$', views.close_account, name='close_account'),
                  url(r'^account/settings/close_account_verification/$', views.close_account_verification,
                      name='close_account_verification'),
                  url(r'^account/password_reset/$', views.password_reset, name='password_reset'),
                  url(r'^account/password_reset_verification/$', views.password_reset_verification,
                      name='password_reset_verification'),
                  url(r'^account/before_password_reset/$', views.before_password_reset, name='before_password_reset'),
                  url(r'^account/regenerate_activation_link/$', views.regenerate_activation_link,
                      name='regenerate_activation_link'),
                  path('ads/', include('ads.urls')),
                  path('pricing/', include('pricing.urls')),
              ] + static(conf_settings.MEDIA_URL, document_root=conf_settings.MEDIA_ROOT)
