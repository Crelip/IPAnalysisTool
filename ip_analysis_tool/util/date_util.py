import datetime
import os
from typing import Tuple
from ..enums import TimeInterval

def get_parent_week(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    """
    Returns the parent week of the given date.
    :param date: Input date.
    :return: The parent week of the given date given as the first and last day of the week.
    """
    monday = date - datetime.timedelta(days=date.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday

def get_parent_month(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    """
    Returns the parent month of the given date.
    :param date: Input date.
    :return: The parent month of the given date given as the first and last day of the month.
    """
    first_day = date.replace(day=1)
    last_day = date.replace(day=28) + datetime.timedelta(days=4)
    last_day = last_day - datetime.timedelta(days=last_day.day)
    return first_day, last_day

def get_parent_year(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    """
    Returns the parent year of the given date.
    :param date: Input date.
    :return: The parent year of the given date given as the first and last day of the year.
    """
    first_day = date.replace(month=1, day=1)
    last_day = date.replace(month=12, day=31)
    return first_day, last_day

def get_parent_interval(date : datetime.date, time_interval : TimeInterval) -> Tuple[datetime.date, datetime.date]:
    """
    Returns the parent interval of the given date.
    :param date: Input date.
    :param time_interval: Specified time interval.
    :return: The parent interval of the given date given as the first and last day of the interval.
    """
    if time_interval == TimeInterval.WEEK:
        return get_parent_week(date)
    elif time_interval == TimeInterval.MONTH:
        return get_parent_month(date)
    elif time_interval == TimeInterval.YEAR:
        return get_parent_year(date)
    elif time_interval == TimeInterval.ALL:
        from .database_util import get_database_range
        return get_database_range()


def iterate_range(start_date : datetime.date, end_date : datetime.date, time_interval : TimeInterval = TimeInterval.WEEK) -> list:
    """
    Returns a list of the given date range based on the given time interval.
    :param start_date: Start date of the range.
    :param end_date: End date of the range.
    :param time_interval: Specified time interval to iterate by.
    :return: A list of the given date range based on the given time interval.
    """
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
    """
    Returns the given date as a string in the (YYYY-MM-DD) format.
    :param date: Input date.
    :return: String of the given date in the (YYYY-MM-DD) format.
    """
    return datetime.datetime.strftime(date, "%Y-%m-%d")

def get_date_object(input: str) -> datetime.date:
    """
    Returns the given date as a datetime.date.
    :param input: Input date as a string in the (YYYY-MM-DD) format.
    :return: Date as a datetime.date.
    """
    return datetime.datetime.strptime(input, "%Y-%m-%d").date()

def get_cache_date_range(weighted = False, time_interval : TimeInterval = TimeInterval.WEEK) -> Tuple[datetime.date, datetime.date]:
    """
    Returns the date range of the graph stored data, by which we mean the earliest and latest date found in the local graph storage.
    :param weighted: Whether we want graphs with weighted edges or not.
    :param time_interval: Time interval to adhere to. Default is TimeInterval.WEEK.
    :return: The earliest and latest date found in the local graph storage.
    """
    files = [f for f in os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/{str(time_interval).lower()}/{'base' if not weighted else 'weighted'}/"))]
    files.sort()
    first_file = files[0]
    last_file = files[-1]
    return get_date_object(first_file.split(".")[0]), get_date_object(last_file.split(".")[0])

def clamp_range(start_1 : datetime.date, end_1 : datetime.date, start_2 : datetime.date, end_2 : datetime.date) -> Tuple[datetime.date, datetime.date]:
    """
    Clamps 2 different date ranges.
    :param start_1: Start date of the 1st range.
    :param end_1: End date of the 1st range.
    :param start_2: Start date of the 2nd range.
    :param end_2: Start date of the 2nd range.
    :return: Clamped date range.
    """
    return max(start_1, start_2), min(end_1, end_2)