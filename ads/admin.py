from django.contrib import admin
from .models import *

# To initialize VersionAdmin "python manage.py createinitialrevisions"
admin.site.register(Ad)
admin.site.register(AdUser)
admin.site.register(AdFile)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(AdFeatured)
admin.site.register(Alert)
admin.site.register(HistoricalFeatured)
