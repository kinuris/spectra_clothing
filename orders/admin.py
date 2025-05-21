from django.contrib import admin
from .models import Customer, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'created_at')
    search_fields = ('name', 'phone_number', 'email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'total_amount', 'created_by')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__name', 'id')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount',)
