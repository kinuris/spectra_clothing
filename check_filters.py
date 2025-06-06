#!/usr/bin/env python
"""
A script to test if dashboard_extras template filters are working correctly.
"""
import os
import sys
import django
from django.template import Template, Context

# First, check the file directly
print('Checking dashboard_extras.py')

with open('dashboard/templatetags/dashboard_extras.py', 'r') as f:
    content = f.read()
    print('File exists and contains:')
    print(content.split('\n')[0:5])
    print('...')
    filters = [line for line in content.split('\n') if '@register.filter' in line]
    print('Registered filters:')
    print(filters)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spectra_clothing.settings')
django.setup()

# Now we can import from our apps
from dashboard.templatetags.dashboard_extras import hash_to_color, dictsumattr

def test_hash_to_color():
    print("\nTesting hash_to_color filter:")
    test_values = ['Men', 'Women', 'Accessories', 'Shoes', 'Hats']
    for value in test_values:
        color = hash_to_color(value)
        print(f"Value: {value}, Color: {color}")
    
    # Test that the same value always produces the same color
    color1 = hash_to_color('Men')
    color2 = hash_to_color('Men')
    print(f"\nConsistency check: 'Men' -> {color1} == {color2}: {color1 == color2}")

def test_dictsumattr():
    print("\nTesting dictsumattr filter:")
    test_data = [
        {'revenue': 100, 'units': 5},
        {'revenue': 200, 'units': 10},
        {'revenue': 300, 'units': 15},
    ]
    
    total_revenue = dictsumattr(test_data, 'revenue')
    total_units = dictsumattr(test_data, 'units')
    
    print(f"Total revenue: {total_revenue}")
    print(f"Total units: {total_units}")

def test_in_template():
    print("\nTesting filters in template rendering:")
    template_string = """
    {% load dashboard_extras %}
    
    Testing hash_to_color:
    {% for item in items %}
    - {{ item }}: {{ item|hash_to_color }}
    {% endfor %}
    
    Testing dictsumattr:
    - Total revenue: ${{ data|dictsumattr:'revenue' }}
    - Total units: {{ data|dictsumattr:'units' }}
    """
    
    template = Template(template_string)
    context = Context({
        'items': ['Men', 'Women', 'Accessories'],
        'data': [
            {'revenue': 100, 'units': 5},
            {'revenue': 200, 'units': 10},
            {'revenue': 300, 'units': 15},
        ]
    })
    
    try:
        rendered = template.render(context)
        print(rendered)
        print("\n✅ Template rendering successful!")
    except Exception as e:
        print(f"\n❌ Template rendering failed: {e}")

if __name__ == "__main__":
    print("Testing dashboard_extras template filters")
    test_hash_to_color()
    test_dictsumattr()
    test_in_template()
