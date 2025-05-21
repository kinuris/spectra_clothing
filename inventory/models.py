from django.db import models
from products.models import Product

class Size(models.Model):
    name = models.CharField(max_length=20)  # e.g., S, M, L, XL, XXL
    
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7, blank=True, null=True)  # e.g., #FF5733
    
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    
    class Meta:
        unique_together = ['product', 'size', 'color']
    
    def __str__(self):
        return f"{self.product.name} - {self.size.name} - {self.color.name}"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

class InventoryAdjustment(models.Model):
    INCOMING = 'incoming'
    OUTGOING = 'outgoing'
    ADJUSTMENT = 'adjustment'
    
    ADJUSTMENT_TYPE_CHOICES = [
        (INCOMING, 'Incoming Stock'),
        (OUTGOING, 'Outgoing Stock'),
        (ADJUSTMENT, 'Stock Adjustment'),
    ]
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPE_CHOICES)
    quantity = models.IntegerField()  # Can be positive or negative
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.get_adjustment_type_display()} - {self.variant} - {self.quantity}"
