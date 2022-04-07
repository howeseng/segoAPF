from django.contrib import admin

# Register your models here.

from .models import *
from .models import Commodity
from .models import Farmer



admin.site.register(Support)
admin.site.register(Profile)
admin.site.register(Commodity)
admin.site.register(Farmer)