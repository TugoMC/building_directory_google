# templatetags/reservation_tags.py
from django import template
from datetime import datetime

register = template.Library()

@register.filter
def format_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d/%m/%Y')