# Generated manually

from django.db import migrations
from decimal import Decimal

def add_sample_products(apps, schema_editor):
    # Get the models from the app registry
    Product = apps.get_model('products', 'Product')
    Category = apps.get_model('products', 'Category')
    ProductImage = apps.get_model('products', 'ProductImage')
    Supplier = apps.get_model('suppliers', 'Supplier')
    
    # Get or create suppliers first
    suppliers = {
        'textile_experts': None,
        'fashion_wholesale': None,
        'eco_fabrics': None,
        'premium_materials': None
    }
    
    # Create suppliers if they don't exist
    sample_suppliers = [
        {
            'key': 'textile_experts',
            'name': 'Textile Experts Co.',
            'contact_person': 'Robert Mills',
            'email': 'rmills@textileexperts.com',
            'phone_number': '555-111-2222',
            'address': '100 Industry Way, Manufacturing District, CA 90001'
        },
        {
            'key': 'fashion_wholesale',
            'name': 'Fashion Wholesale Ltd.',
            'contact_person': 'Jennifer Lopez',
            'email': 'jlopez@fashionwholesale.com',
            'phone_number': '555-222-3333',
            'address': '200 Commerce Blvd, Business Park, CA 90002'
        },
        {
            'key': 'eco_fabrics',
            'name': 'Eco-Friendly Fabrics',
            'contact_person': 'Andrew Green',
            'email': 'agreen@ecofabrics.com',
            'phone_number': '555-333-4444',
            'address': '300 Sustainability Rd, Green Valley, CA 90003'
        },
        {
            'key': 'premium_materials',
            'name': 'Premium Materials Inc.',
            'contact_person': 'Sophia Chen',
            'email': 'schen@premiummaterials.com',
            'phone_number': '555-444-5555',
            'address': '400 Luxury Lane, Highend District, CA 90004'
        }
    ]
    
    for supplier_data in sample_suppliers:
        key = supplier_data.pop('key')
        supplier, created = Supplier.objects.get_or_create(
            name=supplier_data['name'],
            defaults=supplier_data
        )
        suppliers[key] = supplier
    
    # Get all categories
    categories = {}
    for category in Category.objects.all():
        categories[category.name] = category
        categories[category.name.lower()] = category  # Also add lowercase version
    
    # Sample products with their variants
    sample_products = [
        {
            'name': 'Classic Cotton T-shirt',
            'sku': 'TS-CLASSIC-001',
            'category': 'T-shirt',
            'supplier': 'textile_experts',
            'cost_price': '8.50',
            'selling_price': '19.99',
            'description': 'A comfortable classic-fit cotton t-shirt for everyday wear. Made from 100% premium cotton for breathability and durability.',
        },
        {
            'name': 'Graphic Print T-shirt',
            'sku': 'TS-GRAPHIC-001',
            'category': 'T-shirt',
            'supplier': 'fashion_wholesale',
            'cost_price': '10.50',
            'selling_price': '24.99',
            'description': 'Eye-catching graphic print t-shirt. Made from soft cotton blend with a relaxed fit.',
        },
        {
            'name': 'Cropped Cotton T-shirt',
            'sku': 'TS-CROPPED-001',
            'category': 'Cropped Shirt',
            'supplier': 'eco_fabrics',
            'cost_price': '12.75',
            'selling_price': '29.99',
            'description': 'Stylish cropped t-shirt with shorter length. Perfect for summer with high-waisted bottoms.',
        },
        {
            'name': 'Printed Cropped Shirt',
            'sku': 'TS-CROPPED-002',
            'category': 'Cropped Shirt',
            'supplier': 'fashion_wholesale',
            'cost_price': '14.50',
            'selling_price': '32.99',
            'description': 'Fashion-forward cropped shirt with trendy prints. Features a boxy silhouette and raw-edge hem.',
        }
    ]
    
    for product_data in sample_products:
        category_name = product_data.pop('category')
        supplier_key = product_data.pop('supplier')
        
        # Convert string prices to Decimal
        product_data['cost_price'] = Decimal(product_data['cost_price'])
        product_data['selling_price'] = Decimal(product_data['selling_price'])
        
        # Check if product already exists
        if not Product.objects.filter(name=product_data['name']).exists():
            # Create the product with all fields except SKU
            sku = product_data.pop('sku')  # Remove SKU field as it's no longer in the model
            product = Product.objects.create(
                category=categories[category_name],
                supplier=suppliers[supplier_key],
                **product_data
            )
            
            # Add a dummy product image
            ProductImage.objects.create(
                product=product,
                image='products/placeholder.jpg',
                is_primary=True
            )


def add_sample_variants(apps, schema_editor):
    # Get the models
    Product = apps.get_model('products', 'Product')
    Size = apps.get_model('inventory', 'Size')
    Color = apps.get_model('inventory', 'Color')
    ProductVariant = apps.get_model('inventory', 'ProductVariant')
    InventoryAdjustment = apps.get_model('inventory', 'InventoryAdjustment')
    
    # Get the sizes and colors
    sizes = {size.name: size for size in Size.objects.all()}
    colors = {color.name: color for color in Color.objects.all()}
    
    # For each product, create variants
    for product in Product.objects.all():
        # Determine which sizes and colors to use based on product category
        product_sizes = []
        product_colors = []
        
        if product.category.name == 'T-shirt':
            product_sizes = ['S', 'M', 'L', 'XL']
            product_colors = ['Black', 'White', 'Blue', 'Red', 'Gray']
        elif product.category.name == 'Cropped Shirt':
            product_sizes = ['XS', 'S', 'M', 'L']
            product_colors = ['Black', 'White', 'Pink', 'Green', 'Yellow']
        else:
            # Default sizes and colors for other categories
            product_sizes = ['S', 'M', 'L']
            product_colors = ['Black', 'White', 'Blue']
        
        # Create variants for each size-color combination
        for size_name in product_sizes:
            for color_name in product_colors:
                # Skip if variant already exists
                if ProductVariant.objects.filter(
                    product=product,
                    size=sizes[size_name],
                    color=colors[color_name]
                ).exists():
                    continue
                
                # Generate random stock quantity between 5 and 30
                import random
                quantity = random.randint(5, 30)
                
                # Create the variant
                variant = ProductVariant.objects.create(
                    product=product,
                    size=sizes[size_name],
                    color=colors[color_name],
                    quantity=quantity,
                    reorder_level=5
                )
                
                # Create inventory adjustment record
                InventoryAdjustment.objects.create(
                    variant=variant,
                    adjustment_type='incoming',
                    quantity=quantity,
                    notes=f'Initial inventory for {product.name} - {size_name}/{color_name}'
                )


def remove_sample_data(apps, schema_editor):
    # Get models
    Product = apps.get_model('products', 'Product')
    Supplier = apps.get_model('suppliers', 'Supplier')
    
    # Sample product names and supplier names to remove
    sample_product_names = [
        'Classic Cotton T-shirt',
        'Graphic Print T-shirt',
        'Cropped Cotton T-shirt',
        'Printed Cropped Shirt'
    ]
    
    sample_suppliers = [
        'Textile Experts Co.',
        'Fashion Wholesale Ltd.',
        'Eco-Friendly Fabrics',
        'Premium Materials Inc.'
    ]
    
    # Delete products and suppliers
    Product.objects.filter(name__in=sample_product_names).delete()
    Supplier.objects.filter(name__in=sample_suppliers).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_add_default_categories'),
        ('inventory', '0002_add_default_sizes_colors'),
        ('suppliers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_sample_products,
            remove_sample_data
        ),
        migrations.RunPython(
            add_sample_variants,
            remove_sample_data
        ),
    ]
