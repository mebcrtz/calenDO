from django.contrib import admin
from . models import *
# Register your models here.

admin.site.register(Task)
admin.site.register(Schedule)
admin.site.register(Item)
admin.site.register(ItemOccurrence)
