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
                product.name = f"{product.name} ({product.sku})"
                product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_add_sample_products'),
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
