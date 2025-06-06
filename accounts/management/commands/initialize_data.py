from django.core.management.base import BaseCommand
from accounts.models import User
from products.models import Category
from inventory.models import Size, Color
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Initialize the database with basic data needed for the application'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to initialize data...'))
        
        # Create default admin user
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@spectrastore.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    role=User.ADMIN
                )
                self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
            else:
                self.stdout.write(self.style.WARNING('Admin user already exists.'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}'))

        # Create default users for each role
        try:
            if not User.objects.filter(username='joven').exists():
                User.objects.create_user(
                    username='joven',
                    email='joven@spectrastore.com',
                    password='joven123',
                    first_name='Joven',
                    last_name='Alovera',
                    role=User.STOCK_MANAGER
                )
                self.stdout.write(self.style.SUCCESS('Stock Manager user created successfully!'))
            else:
                self.stdout.write(self.style.WARNING('Stock Manager user already exists.'))
                
            if not User.objects.filter(username='villy').exists():
                User.objects.create_user(
                    username='villy',
                    email='villy@spectrastore.com',
                    password='villy123',
                    first_name='Villy',
                    last_name='Delsocora',
                    role=User.SALES
                )
                self.stdout.write(self.style.SUCCESS('Sales user created successfully!'))
            else:
                self.stdout.write(self.style.WARNING('Sales user already exists.'))
                
            if not User.objects.filter(username='jeanny').exists():
                User.objects.create_user(
                    username='jeanny',
                    email='jeanny@spectrastore.com',
                    password='jeanny123',
                    first_name='Jeanny',
                    last_name='Escalada',
                    role=User.ADMIN
                )
                self.stdout.write(self.style.SUCCESS('Owner admin user created successfully!'))
            else:
                self.stdout.write(self.style.WARNING('Owner admin user already exists.'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating users: {str(e)}'))
            
        # Create product categories
        categories = ['T-shirt', 'Cropped Shirt']
        for category_name in categories:
            try:
                Category.objects.get_or_create(name=category_name)
                self.stdout.write(self.style.SUCCESS(f'Category "{category_name}" created or verified.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating category {category_name}: {str(e)}'))
                
        # Create standard sizes
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        for size_name in sizes:
            try:
                Size.objects.get_or_create(name=size_name)
                self.stdout.write(self.style.SUCCESS(f'Size "{size_name}" created or verified.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating size {size_name}: {str(e)}'))
                
        # Create standard colors
        colors = [
            {'name': 'Black', 'color_code': '#000000'},
            {'name': 'White', 'color_code': '#FFFFFF'},
            {'name': 'Red', 'color_code': '#FF0000'},
            {'name': 'Blue', 'color_code': '#0000FF'},
            {'name': 'Green', 'color_code': '#008000'},
            {'name': 'Yellow', 'color_code': '#FFFF00'},
            {'name': 'Purple', 'color_code': '#800080'},
            {'name': 'Pink', 'color_code': '#FFC0CB'},
            {'name': 'Gray', 'color_code': '#808080'},
            {'name': 'Brown', 'color_code': '#A52A2A'},
        ]
        
        for color_data in colors:
            try:
                Color.objects.get_or_create(
                    name=color_data['name'],
                    defaults={'color_code': color_data['color_code']}
                )
                self.stdout.write(self.style.SUCCESS(f'Color "{color_data["name"]}" created or verified.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating color {color_data["name"]}: {str(e)}'))
                
        self.stdout.write(self.style.SUCCESS('Data initialization completed successfully!'))
