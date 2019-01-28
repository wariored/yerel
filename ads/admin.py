from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import *

# To initialize VersionAdmin "python manage.py createinitialrevisions"
admin.site.register(Ad, VersionAdmin)
admin.site.register(AdUser, VersionAdmin)
admin.site.register(AdFile, VersionAdmin)
admin.site.register(Category, VersionAdmin)
admin.site.register(Location, VersionAdmin)
