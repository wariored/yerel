from django.contrib import admin
from .models import *
from reversion.admin import VersionAdmin

admin.site.register(Pricing, VersionAdmin)
