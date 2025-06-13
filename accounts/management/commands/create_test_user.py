from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create a test user for middleware testing'

    def handle(self, *args, **options):
        # Check if test user already exists
        if User.objects.filter(username='testuser').exists():
            self.stdout.write(
                self.style.WARNING('Test user already exists')
            )
            return

        # Create test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='admin'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created test user: {user.username}')
        )
