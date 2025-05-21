from django.contrib import admin
from .models import SalesReport, TopSellingProduct

class TopSellingProductInline(admin.TabularInline):
    model = TopSellingProduct
    extra = 1

@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'date_from', 'date_to', 'total_sales', 'total_orders', 'generated_at')
    list_filter = ('report_type', 'generated_at')
    inlines = [TopSellingProductInline]
