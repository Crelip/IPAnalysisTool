import datetime
from typing import Tuple
def getWeek(date : datetime.date) -> Tuple[datetime.date, datetime.date]:
    monday = date - datetime.timedelta(days=date.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday

def getWeekDates(startDate : datetime.date, endDate : datetime.date) -> list:
    weeks = []
    currentMonday, currentSunday = getWeek(startDate)
    while currentMonday <= endDate:
        weeks.append((currentMonday, currentSunday))
        currentMonday += datetime.timedelta(weeks=1)
        currentSunday = currentMonday + datetime.timedelta(days=6)
    return weeks