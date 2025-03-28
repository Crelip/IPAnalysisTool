import datetime
import os
from typing import Tuple
from ..enums import TimeInterval

def get_parent_week(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    monday = date - datetime.timedelta(days=date.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday

def get_parent_month(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    first_day = date.replace(day=1)
    last_day = date.replace(day=28) + datetime.timedelta(days=4)
    last_day = last_day - datetime.timedelta(days=last_day.day)
    return first_day, last_day

def get_parent_year(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    first_day = date.replace(month=1, day=1)
    last_day = date.replace(month=12, day=31)
    return first_day, last_day

def get_parent_interval(date : datetime.date, time_interval : TimeInterval) -> Tuple[datetime.date, datetime.date]:
    if time_interval == TimeInterval.WEEK:
        return get_parent_week(date)
    elif time_interval == TimeInterval.MONTH:
        return get_parent_month(date)
    elif time_interval == TimeInterval.YEAR:
        return get_parent_year(date)
    elif time_interval == TimeInterval.ALL:
        from .database_util import get_database_range
        return get_database_range()

# Deprecated
def iterate_weekly(start_date : datetime.date, end_date : datetime.date) -> list:
    weeks = []
    current_monday, current_sunday = get_parent_week(start_date)
    while current_monday <= end_date:
        weeks.append((current_monday, current_sunday))
        current_monday += datetime.timedelta(weeks=1)
        current_sunday = current_monday + datetime.timedelta(days=6)
    return weeks

def iterate_range(start_date : datetime.date, end_date : datetime.date, time_interval : TimeInterval = TimeInterval.WEEK) -> list:
    from dateutil.relativedelta import relativedelta
    intervals = []
    if time_interval == TimeInterval.WEEK:
        delta = relativedelta(weeks=1)
        current_first, current_last = get_parent_week(start_date)
    elif time_interval == TimeInterval.MONTH:
        delta = relativedelta(months=1)
        current_first, current_last = get_parent_month(start_date)
    elif time_interval == TimeInterval.YEAR:
        delta = relativedelta(years=1)
        current_first, current_last = get_parent_year(start_date)
    elif time_interval == TimeInterval.ALL:
        from .database_util import get_database_range
        return [get_database_range()]

    while current_first <= end_date:
        intervals.append((current_first, current_last))
        current_first += delta
        if time_interval == TimeInterval.WEEK: current_first, current_last = get_parent_week(current_first)
        elif time_interval == TimeInterval.MONTH: current_first, current_last = get_parent_month(current_first)
        elif time_interval == TimeInterval.YEAR: current_first, current_last = get_parent_year(current_first)
    return intervals

def get_date_string(date: datetime.date) -> str:
    return datetime.datetime.strftime(date, "%Y-%m-%d")

def get_date_object(input: str) -> datetime.date:
    return datetime.datetime.strptime(input, "%Y-%m-%d").date()

def get_cache_date_range(weighted = False, time_interval : TimeInterval = TimeInterval.WEEK):
    files = [f for f in os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/{str(time_interval).lower()}/{'base' if not weighted else 'weighted'}/"))]
    files.sort()
    first_file = files[0]
    last_file = files[-1]
    return get_date_object(first_file.split(".")[0]), get_date_object(last_file.split(".")[0])