from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely gets a dictionary item by key."""
    if isinstance(dictionary, dict):
        if isinstance(key, str):
            return dictionary.get(key, 0)  # Default to 0 if the key doesn't exist
        elif hasattr(key, 'name'):  # Handle LeaveType model instance
            return dictionary.get(key.name, 0)  # Use the name field of the model
    return 0  # Return 0 if the dictionary or key is not valid


@register.filter
def get_range(value):
    """Returns a range of numbers up to the given value."""
    return range(1, value + 1)  # To ensure the range starts from 1

from django import template

register = template.Library()

@register.filter
def dict(value, key):
    """Return the value for the given key in a dictionary."""
    return value.get(key) if isinstance(value, dict) else None
