from django.contrib import admin
from .models import Ad, DailyVisitor, Location
# Register your models here.


admin.site.register(Ad)
admin.site.register(DailyVisitor)
admin.site.register(Location)