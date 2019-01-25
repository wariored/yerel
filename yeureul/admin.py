from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import *


@admin.register(UserInfo)
class UserInfoAdmin(VersionAdmin):
    pass


@admin.register(UserKey)
class UserKeyAdmin(VersionAdmin):
    pass


@admin.register(ContactMessage)
class ContactMessageAdmin(VersionAdmin):
    pass

