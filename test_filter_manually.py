#!/usr/bin/env python
"""
A simpler script to test filter loading directly.
"""
import os
import django
import hashlib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spectra_clothing.settings')
django.setup()

# Manually test the hash_to_color function
def hash_to_color(value):
    """
    Converts a value to a consistent color by hashing
    """
    colors = [
        'rgba(79, 70, 229, 0.8)',  # Indigo
        'rgba(16, 185, 129, 0.8)',  # Green
        'rgba(245, 158, 11, 0.8)',  # Yellow
        'rgba(239, 68, 68, 0.8)',   # Red
        'rgba(139, 92, 246, 0.8)',  # Purple
        'rgba(14, 165, 233, 0.8)',  # Light Blue
        'rgba(236, 72, 153, 0.8)',  # Pink
        'rgba(249, 115, 22, 0.8)',  # Orange
    ]
    
    # Generate a hash of the value and map it to a color index
    hash_obj = hashlib.md5(str(value).encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    color_index = hash_int % len(colors)
    
    return colors[color_index]

# Test it
test_values = ['Men', 'Women', 'Accessories', 'Shoes', 'Hats']
for value in test_values:
    color = hash_to_color(value)
    print(f"Value: {value}, Color: {color}")

# Print a message for users to run the server and test
print("\nTo test in the browser:")
print("1. Make sure you're in a virtual environment with Django installed")
print("2. Run: python3 manage.py runserver")
print("3. Open http://127.0.0.1:8000/dashboard/analytics/ in your browser")
print("4. Inspect the category colors in the visualization")
