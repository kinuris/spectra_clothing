from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'admin'
    STOCK_MANAGER = 'stock_manager'
    SALES = 'sales'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (STOCK_MANAGER, 'Stock Manager'),
        (SALES, 'Sales Staff'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SALES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    
    @property
    def is_stock_manager(self):
        return self.role == self.STOCK_MANAGER
    
    @property
    def is_sales(self):
        return self.role == self.SALES
