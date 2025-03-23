import datetime
import os
from typing import Tuple
def get_week(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    monday = date - datetime.timedelta(days=date.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday

def get_week_dates(start_date : datetime.date, end_date : datetime.date) -> list:
    weeks = []
    current_monday, current_sunday = get_week(start_date)
    while current_monday <= end_date:
        weeks.append((current_monday, current_sunday))
        current_monday += datetime.timedelta(weeks=1)
        current_sunday = current_monday + datetime.timedelta(days=6)
    return weeks

def get_date_string(date: datetime.date) -> str:
    return datetime.datetime.strftime(date, "%Y-%m-%d")

def get_date_object(input: str) -> datetime.date:
    return datetime.datetime.strptime(input, "%Y-%m-%d").date()

def get_cache_date_range(weighted = False):
    files = [f for f in os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{'base' if not weighted else 'weighted'}/"))]
    files.sort()
    first_file = files[0]
    last_file = files[-1]
    return get_date_object(first_file.split(".")[0]), get_date_object(last_file.split(".")[0])