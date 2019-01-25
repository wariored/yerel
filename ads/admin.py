from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *
admin.site.register(Ad , SimpleHistoryAdmin)
admin.site.register(AdUser, SimpleHistoryAdmin)
admin.site.register(AdFile, SimpleHistoryAdmin)
admin.site.register(Category, SimpleHistoryAdmin)
admin.site.register(Location , SimpleHistoryAdmin)