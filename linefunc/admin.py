from django.contrib import admin
from .models import *
# Register your models here.

class Order_Admin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.get_fields()]
    ordering = ('-order_time',)
class Store_Admin(admin.ModelAdmin):
    list_display =('category','name')

class Store_food_Admin(admin.ModelAdmin):
    list_display =('__str__','online','start_time')
    
admin.site.register(User)
admin.site.register(Store_food,Store_food_Admin)
admin.site.register(Store,Store_Admin)
admin.site.register(Order,Order_Admin)
