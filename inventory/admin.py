from django.contrib import admin
from inventory.models import Order, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'group', 'quantity', 'price')
    ordering = ('group',)
    search_fields = ('name', 'group', 'code')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'status')
    ordering = ('-created_date',)
    search_fields = ('name', 'code', 'status')
# admin.site.register(Order)
# admin.site.register(Item)

# Register your models here.
