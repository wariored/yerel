from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *
admin.site.register(UserInfo , SimpleHistoryAdmin)
admin.site.register(UserKey, SimpleHistoryAdmin)
admin.site.register(ContactMessage, SimpleHistoryAdmin)
