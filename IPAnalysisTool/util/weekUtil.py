import datetime
import os
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

def getDateString(date: datetime.date) -> str:
    return datetime.datetime.strftime(date, "%Y-%m-%d")

def getDateObject(input: str) -> datetime.date:
    return datetime.datetime.strptime(input, "%Y-%m-%d").date()

def getCacheDateRange(weighted = False):
    files = [f for f in os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{'base' if not weighted else 'weighted'}/"))]
    files.sort()
    firstFile = files[0]
    lastFile = files[-1]
    return getDateObject(firstFile.split(".")[0]), getDateObject(lastFile.split(".")[0])