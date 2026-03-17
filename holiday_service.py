from datetime import date, timedelta
import calendar
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


from datetime import date, timedelta

def get_us_holidays(year: int, month: int = None) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "New Year's Day"),
        (6, 19, "Juneteenth National Independence Day"),
        (7, 4, "Independence Day"),
        (11, 11, "Veterans Day"),
        (12, 25, "Christmas Day"),
    )

    nth_weekday_holidays = (
        (1, 3, 1, "Martin Luther King Jr. Day"),
        (2, 3, 1, "Washington's Birthday"),
        (5, -1, 1, "Memorial Day"),
        (9, 1, 1, "Labor Day"),
        (10, 2, 1, "Columbus Day"),
        (11, 4, 4, "Thanksgiving Day"),
    )

    holidays = []

    # 1) 고정 휴일 추가 + observed 추가
    for mm, dd, name in fixed_holidays:
        actual_day = date(year, mm, dd)
        holidays.append(Holiday("US", actual_day, name))

        if actual_day.isoweekday() == 6:  # Saturday
            observed_day = actual_day - timedelta(days=1)
            holidays.append(Holiday("US", observed_day, name, "Observed"))
        elif actual_day.isoweekday() == 7:  # Sunday
            observed_day = actual_day + timedelta(days=1)
            holidays.append(Holiday("US", observed_day, name, "Observed"))

    # 2) 요일 기반 휴일 추가
    for mm, n, weekday, name in nth_weekday_holidays:
        if n == -1:
            holiday_day = last_weekday_of_month(year, mm, weekday)
        else:
            holiday_day = nth_weekday_of_month(year, mm, weekday, n)

        holidays.append(Holiday("US", holiday_day, name))

    # 3) 연 필터
    holidays = [holiday for holiday in holidays if holiday.day.year == year]

    # 4) 월 필터
    if month is not None:
        holidays = [holiday for holiday in holidays if holiday.day.month == month]

    return holidays


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    # 특정 년/월의 n번째 특정 요일 날짜 반환
    # weekday: isoweekday 기준 (1=Mon, ..., 7=Sun)

    if not 1 <= weekday <= 7:
        raise ValueError("weekday는 1~7 사이여야 합니다.")
    if n < 1:
        raise ValueError("n은 1 이상이어야 합니다.")

    first_weekday = date(year, month, 1).isoweekday()
    offset = (weekday - first_weekday + 7) % 7
    target_day = 1 + offset + (n - 1) * 7

    return date(year, month, target_day)

    
def last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    # 특정 년/월의 마지막 특정 요일 날짜 반환
    # weekday: isoweekday 기준 (1=Mon, ..., 7=Sun)

    if not 1 <= weekday <= 7:
        raise ValueError("weekday는 1~7 사이여야 합니다.")

    last_day = calendar.monthrange(year, month)[1] 
    last_date = date(year, month, last_day)
    last_date_weekday = last_date.isoweekday()

    offset = (last_date_weekday - weekday + 7) % 7
    target_day = last_day - offset

    return date(year, month, target_day)


def get_holidays_by_query(query: Query) -> list[Holiday]:
    holidays = []

    if query.country == "KR":
        holidays.extend(get_kr_holidays(query.year, query.month))

    elif query.country == "US":
        holidays.extend(get_us_holidays(query.year, query.month))

    else:
        holidays.extend(get_kr_holidays(query.year, query.month))
        holidays.extend(get_us_holidays(query.year, query.month))

    holidays.sort(key=lambda holiday: (holiday.day, holiday.country, holiday.name))
    return holidays

    