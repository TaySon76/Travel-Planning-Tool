from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(UserProfile)
admin.site.register(AdditionalData)
admin.site.register(Trip)
admin.site.register(SharedTrip)
admin.site.register(Budget)
admin.site.register(BudgetItem)
admin.site.register(City)