from datetime import date
from models import Holiday, Query


def get_kr_holidays(year: int, month: int=None) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "신정"),
        (3, 1, "삼일절"),
        (5, 5, "어린이날"),
        (6, 6, "현충일"),
        (8, 15, "광복절"),
        (10, 3, "개천절"),
        (10, 9, "한글날"),
        (12, 25, "성탄절"),
    )

    holidays = []
    if month == None:
        for mm, dd, name in fixed_holidays:
            holidays.append(Holiday("KR", date(year, mm, dd), name))
    else:
        for mm, dd, name in fixed_holidays:
            if month == mm:
                holidays.append(Holiday("KR", date(year, mm, dd), name))

    return holidays


def get_us_holidays(year: int, month: int=None) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "New Year's Day"),
        (6, 19, "Juneteenth National Independence Day"),
        (7, 4, "Independence Day"),
        (11, 11, "Veterans Day"),
        (12, 25, "Christmas Day"),
    )

    holidays = []
    if month == None:
        for mm, dd, name in fixed_holidays:
            holidays.append(Holiday("US", date(year, mm, dd), name))
    else:
        for mm, dd, name in fixed_holidays:
            if month == mm:
                holidays.append(Holiday("US", date(year, mm, dd), name))

    return holidays

def nth_weekday_of_month():
    pass

def last_weekday_of_month():
    pass

def get_holidays_by_query(query: Query) -> list[Holiday]:

    holidays = []
    if query.country == "KR":
        holidays.extend(get_kr_holidays(query.year, query.month))
        return holidays
    
    elif query.country == "US":
        holidays.extend(get_us_holidays(query.year, query.month))
        return holidays
    
    else:
        holidays.extend(get_kr_holidays(query.year, query.month))
        holidays.extend(get_us_holidays(query.year, query.month))
        return holidays

    