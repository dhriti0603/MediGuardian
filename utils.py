from datetime import datetime, timedelta

def today_str():
    return datetime.now().strftime("%d-%m-%Y")

def now_time_str():
    return datetime.now().strftime("%H:%M")

def now_full_str():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def validate_time(value):
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False

def date_range_filter(range_name):
    today = datetime.now()
    if range_name == "Daily":
        return today.strftime("%d-%m-%Y"), today.strftime("%d-%m-%Y")
    if range_name == "Weekly":
        start = today - timedelta(days=6)
        return start.strftime("%d-%m-%Y"), today.strftime("%d-%m-%Y")
    if range_name == "Monthly":
        start = today - timedelta(days=29)
        return start.strftime("%d-%m-%Y"), today.strftime("%d-%m-%Y")
    return None, None

def parse_date(date_text):
    return datetime.strptime(date_text, "%d-%m-%Y")
