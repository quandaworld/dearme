from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def time_since(value):
    """Format a datetime as a time since string (e.g., '2 years ago')"""
    if not value:
        return ''
    
    now = timezone.now()
    diff = now - value
    
    # Convert to days
    days = diff.days
    
    if days <= 0:
        # For very recent items
        hours = diff.seconds // 3600
        if hours <= 0:
            minutes = diff.seconds // 60
            if minutes <= 0:
                return 'just now'
            elif minutes == 1:
                return '1 minute ago'
            else:
                return f'{minutes} minutes ago'
        elif hours == 1:
            return '1 hour ago'
        else:
            return f'{hours} hours ago'
    elif days == 1:
        return 'yesterday'
    elif days < 7:
        return f'{days} days ago'
    elif days < 31:
        weeks = days // 7
        if weeks == 1:
            return '1 week ago'
        else:
            return f'{weeks} weeks ago'
    elif days < 365:
        months = days // 30  # Approximate
        if months == 1:
            return '1 month ago'
        else:
            return f'{months} months ago'
    else:
        years = days // 365
        if years == 1:
            return '1 year ago'
        else:
            return f'{years} years ago'

@register.filter
def date_format(value, format_string="%B %d, %Y"):
    """Format a date according to the given format"""
    if not value:
        return ''
    
    if isinstance(value, datetime):
        return value.strftime(format_string)
    
    return value
