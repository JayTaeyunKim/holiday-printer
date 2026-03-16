from datetime import date
from models import Holiday, Query


def get_kr_holidays(year: int) -> list[Holiday]:
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
    for month, day, name in fixed_holidays:
        holidays.append(Holiday("KR", date(year, month, day), name))

    return holidays


def get_us_holidays(year: int) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "New Year's Day"),
        (6, 19, "Juneteenth National Independence Day"),
        (7, 4, "Independence Day"),
        (11, 11, "Veterans Day"),
        (12, 25, "Christmas Day"),
    )

    holidays = []
    for month, day, name in fixed_holidays:
        holidays.append(Holiday("US", date(year, month, day), name))

    return holidays

def get_holidays_by_query(query: Query) -> list[Holiday]:
    pass