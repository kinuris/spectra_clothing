# Generated manually

from django.db import migrations
import datetime
import random
from decimal import Decimal

def add_sample_orders(apps, schema_editor):
    # Get the models from the app registry
    Order = apps.get_model('orders', 'Order')
    OrderItem = apps.get_model('orders', 'OrderItem')
    Customer = apps.get_model('orders', 'Customer')
    ProductVariant = apps.get_model('inventory', 'ProductVariant')
    InventoryAdjustment = apps.get_model('inventory', 'InventoryAdjustment')
    User = apps.get_model('accounts', 'User')
    
    # Try to get sales and admin users for creating orders
    try:
        sales_user = User.objects.filter(role='sales').first()
        admin_user = User.objects.filter(role='admin').first()
    except:
        sales_user = None
        admin_user = None
    
    # Get all customers
    customers = list(Customer.objects.all())
    if not customers:
        # No customers to create orders for
        return
    
    # Get all product variants with stock
    variants = list(ProductVariant.objects.filter(quantity__gt=0))
    if not variants:
        # No variants with stock
        return
    
    # Generate orders in the past 30 days
    today = datetime.date.today()
    
    # Sample order data
    sample_orders = [
        {
            'customer': random.choice(customers),
            'status': random.choice(['pending', 'processing', 'shipped', 'delivered']),
            'notes': random.choice(['Please deliver in the morning.', 'Gift wrap requested.', 'Call before delivery.', '']),
            'days_ago': random.randint(0, 30),  # Random day in the past month
            'created_by': random.choice([sales_user, admin_user]) if sales_user and admin_user else None,
            'items_count': random.randint(1, 4)  # Random number of items per order
        } for _ in range(15)  # Create 15 sample orders
    ]
    
    for order_data in sample_orders:
        # Extract data
        customer = order_data.pop('customer')
        status = order_data.pop('status')
        notes = order_data.pop('notes')
        days_ago = order_data.pop('days_ago')
        created_by = order_data.pop('created_by')
        items_count = order_data.pop('items_count')
        
        # Create order with backdated order_date
        order_date = today - datetime.timedelta(days=days_ago)
        
        # Create the order
        order = Order.objects.create(
            customer=customer,
            status=status,
            notes=notes,
            created_by=created_by
        )
        
        # Update order date directly in database to backdate
        Order.objects.filter(id=order.id).update(
            order_date=order_date
        )
        
        # Add random items to the order
        selected_variants = random.sample(variants, min(items_count, len(variants)))
        for variant in selected_variants:
            # Determine quantity (1-3 items per variant)
            quantity = random.randint(1, 3)
            
            # Make sure we don't exceed available stock
            quantity = min(quantity, variant.quantity)
            if quantity <= 0:
                continue
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                quantity=quantity,
                price=variant.product.selling_price
            )
            
            # Create inventory adjustment for the outgoing stock
            InventoryAdjustment.objects.create(
                variant=variant,
                adjustment_type='outgoing',
                quantity=quantity,
                notes=f'Order #{order.id}',
                created_by=created_by
            )
            
            # Update variant quantity
            new_quantity = variant.quantity - quantity
            ProductVariant.objects.filter(id=variant.id).update(quantity=new_quantity)
            variant.quantity = new_quantity  # Update in-memory model for future iterations


def remove_sample_orders(apps, schema_editor):
    # Get the Order model
    Order = apps.get_model('orders', 'Order')
    
    # Delete all orders (will cascade to order items)
    # In a real production environment, you might want to be more selective
    Order.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_add_sample_customers'),
        ('products', '0003_add_sample_products'),
    ]

    operations = [
        migrations.RunPython(
            add_sample_orders,
            remove_sample_orders
        ),
    ]
