# Generated manually

from django.db import migrations, models

def transfer_sku_to_name_if_needed(apps, schema_editor):
    """For products where name is not unique, make it unique by appending SKU"""
    Product = apps.get_model('products', 'Product')
    
    # Get all products
    products = list(Product.objects.all())
    seen_names = {}
    
    # First pass: identify duplicate names
    for product in products:
        if product.name in seen_names:
            seen_names[product.name].append(product)
        else:
            seen_names[product.name] = [product]
    
    # Second pass: resolve duplicates by appending SKU
    for name, product_list in seen_names.items():
        if len(product_list) > 1:
            for product in product_list:
                # Use a unique identifier if SKU is not available
                # Just add some number suffix to make it unique
                product.name = f"{product.name} (Item {product.id})"
                product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_add_default_categories'),
    ]

    operations = [
        # First run the function to ensure all product names are unique
        migrations.RunPython(
            transfer_sku_to_name_if_needed,
            migrations.RunPython.noop
        ),
        
        # Make the name field unique and increase its max length
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        
        # Remove the SKU field
        migrations.RemoveField(
            model_name='product',
            name='sku',
        ),
    ]
