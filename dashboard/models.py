from django.db import models
from django.utils import timezone
from products.models import Product
from inventory.models import ProductVariant

class SalesReport(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    
    REPORT_TYPE_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
    ]
    
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    date_from = models.DateField()
    date_to = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    # These properties will be calculated on-the-fly and won't be stored in the database
    @property
    def average_order_value(self):
        if self.total_orders > 0:
            return self.total_sales / self.total_orders
        return None
    
    @property
    def daily_average_sales(self):
        date_delta = (self.date_to - self.date_from).days + 1  # Include both start and end days
        if date_delta > 0:
            return self.total_sales / date_delta
        return self.total_sales  # If it's the same day
    
    def __str__(self):
        return f"{self.get_report_type_display()} Report: {self.date_from} to {self.date_to}"

class TopSellingProduct(models.Model):
    report = models.ForeignKey(SalesReport, on_delete=models.CASCADE, related_name='top_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} - {self.total_quantity} units"
