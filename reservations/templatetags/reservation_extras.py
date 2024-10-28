# reservation/templatetags/reservation_extras.py
from django import template
from datetime import datetime
import json

register = template.Library()

@register.filter
def parse_dates(dates_json):
    """Parse le JSON des dates et retourne une liste de dates formatées"""
    try:
        dates = json.loads(dates_json)
        return [datetime.strptime(date, '%Y-%m-%d').strftime('%d %B %Y') for date in dates]
    except:
        return []
    
    
    
# reservations/templatetags/reservation_extras.py
from django import template
from datetime import datetime
import json

register = template.Library()

@register.filter
def format_selected_dates(value):
    """
    Convertit une chaîne JSON de dates en format lisible en français
    Input: '["2024-10-29","2024-10-30"]'
    Output: '29/10/2024, 30/10/2024'
    """
    try:
        if isinstance(value, str):
            dates = json.loads(value)
        else:
            dates = value
            
        formatted_dates = []
        for date_str in dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_dates.append(date_obj.strftime('%d/%m/%Y'))
            
        return ', '.join(formatted_dates)
    except (json.JSONDecodeError, ValueError):
        return value