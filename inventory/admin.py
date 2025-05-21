from django.contrib import admin
from .models import Size, Color, ProductVariant, InventoryAdjustment

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code')
    search_fields = ('name',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'quantity', 'reorder_level', 'is_low_stock')
    list_filter = ('product__category', 'size', 'color')
    search_fields = ('product__name', 'product__sku')

@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('variant', 'adjustment_type', 'quantity', 'created_at', 'created_by')
    list_filter = ('adjustment_type', 'created_at')
    search_fields = ('variant__product__name', 'notes')
