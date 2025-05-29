from django import template
import hashlib

register = template.Library()

@register.filter
def dictsumattr(value, arg):
    """
    Sums the values of a specific attribute across a list of dictionaries
    """
    return sum(item[arg] for item in value)

@register.filter
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
