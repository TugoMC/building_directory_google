# reservation/utils.py
import calendar
from datetime import datetime, date, timedelta

class CalendarManager:
    def __init__(self, year=None, month=None):
        self.year = year or date.today().year
        self.month = month or date.today().month
        self.calendar = calendar.Calendar()
        
    def get_calendar_data(self, available_days):
        # Get current date info
        current_date = date.today()
        current_day = current_date.day if current_date.year == self.year and current_date.month == self.month else None
        
        # Get all dates for the month
        month_dates = self.calendar.monthdatescalendar(self.year, self.month)
        
        # Get previous month days that appear in the first week
        first_week = month_dates[0]
        previous_month_days = [day.day for day in first_week if day.month != self.month]
        
        # Get all days in current month
        days = []
        available_dates = set()
        
        # Convert available_days from weekday names to dates
        for week in month_dates:
            for day in week:
                if day.month == self.month:
                    days.append(day.day)
                    # Check if this day's weekday matches any available day
                    if day.strftime('%A') in available_days and day >= current_date:
                        available_dates.add(day.day)
        
        return {
            'month_name': calendar.month_name[self.month],
            'year': self.year,
            'days': days,
            'previous_month_days': previous_month_days,
            'current_day': current_day,
            'available_days': available_dates,
        }
