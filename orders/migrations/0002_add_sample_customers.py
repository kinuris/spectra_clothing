# Generated manually

from django.db import migrations

def add_sample_customers(apps, schema_editor):
    # Get the Customer model from the app registry
    Customer = apps.get_model('orders', 'Customer')
    
    # Add sample customers if they don't exist
    sample_customers = [
        {
            'name': 'John Smith',
            'email': 'john.smith@example.com',
            'phone_number': '555-123-4567',
            'address': '123 Main St, Anytown, CA 94121'
        },
        {
            'name': 'Sarah Johnson',
            'email': 'sarah.j@example.com',
            'phone_number': '555-234-5678',
            'address': '456 Oak Ave, Somecity, CA 94122'
        },
        {
            'name': 'Michael Wong',
            'email': 'mwong@example.com',
            'phone_number': '555-345-6789',
            'address': '789 Pine St, Anothercity, CA 94123'
        },
        {
            'name': 'Emily Davis',
            'email': 'emily.davis@example.com',
            'phone_number': '555-456-7890',
            'address': '101 Maple Rd, Newtown, CA 94124'
        },
        {
            'name': 'Jose Rodriguez',
            'email': 'jose.r@example.com',
            'phone_number': '555-567-8901',
            'address': '202 Cedar Blvd, Oldtown, CA 94125'
        },
        {
            'name': 'Emma Wilson',
            'email': 'ewilson@example.com',
            'phone_number': '555-678-9012',
            'address': '303 Elm St, Uptown, CA 94126'
        },
        {
            'name': 'David Kim',
            'email': 'dkim@example.com',
            'phone_number': '555-789-0123',
            'address': '404 Birch Dr, Downtown, CA 94127'
        },
        {
            'name': 'Maria Garcia',
            'email': 'mgarcia@example.com',
            'phone_number': '555-890-1234',
            'address': '505 Willow Lane, Crosstown, CA 94128'
        }
    ]
    
    for customer_data in sample_customers:
        if not Customer.objects.filter(name=customer_data['name'], email=customer_data['email']).exists():
            Customer.objects.create(**customer_data)


def remove_sample_customers(apps, schema_editor):
    # Get the Customer model from the app registry
    Customer = apps.get_model('orders', 'Customer')
    
    # List of sample customer emails to remove
    sample_emails = [
        'john.smith@example.com',
        'sarah.j@example.com',
        'mwong@example.com',
        'emily.davis@example.com',
        'jose.r@example.com',
        'ewilson@example.com',
        'dkim@example.com',
        'mgarcia@example.com'
    ]
    
    # Delete the sample customers
    Customer.objects.filter(email__in=sample_emails).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_sample_customers,
            remove_sample_customers
        ),
    ]
