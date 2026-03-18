from datetime import date, timedelta
import calendar
from models import Holiday, Query
from korean_lunar_calendar import KoreanLunarCalendar
from collections import Counter



def lunar_to_solar(year: int, month: int, day: int, is_leap_month: bool = False) -> date:
    calendar = KoreanLunarCalendar()

    ok = calendar.setLunarDate(year, month, day, is_leap_month)
    if not ok:
        raise ValueError("유효하지 않은 음력 날짜입니다.")

    solar_text = calendar.SolarIsoFormat()   # 예: '2026-02-17'
    y, m, d = map(int, solar_text.split("-"))
    return date(y, m, d)


def is_weekend(d: date) -> bool:
    return d.isoweekday() >= 6  # 6=토, 7=일


def next_non_holiday(start_day: date, occupied_days: set[date]) -> date:
    d = start_day + timedelta(days=1)
    while is_weekend(d) or d in occupied_days:
        d += timedelta(days=1)
    return d


def get_kr_holidays(year: int, month: int = None) -> list[Holiday]:
    # (월, 일, 이름, 시작연도, 종료연도)
    fixed_holidays = (
        (1, 1, "신정", None, None),
        (3, 1, "삼일절", None, None),
        (5, 5, "어린이날", None, None),
        (6, 6, "현충일", None, None),
        (7, 17, "제헌절", 2026, None),
        (8, 15, "광복절", None, None),
        (10, 3, "개천절", None, None),
        (10, 9, "한글날", None, None),
        (12, 25, "성탄절", None, None),
        (6, 3, "9회 지방선거", 2026, 2026),
    )

    # (음력 월, 음력 일, 이름)
    lunar_holidays = (
        (1, 1, "설날"),
        (4, 8, "부처님오신날"),
        (8, 15, "추석"),
    )

    observable_holidays = (
        "설날",
        "추석",
        "부처님오신날",
        "삼일절",
        "어린이날",
        "광복절",
        "개천절",
        "한글날",
    )

    holidays: list[Holiday] = []

    # 1) 고정 휴일 생성
    for mm, dd, name, start_year, end_year in fixed_holidays:
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        holidays.append(Holiday("KR", date(year, mm, dd), name))

    # 2) 음력 휴일 생성
    holiday_groups: list[tuple[str, list[date]]] = []

    for mm, dd, name in lunar_holidays:
        solar_day = lunar_to_solar(year, mm, dd)

        if name == "설날":
            group_days = [
                solar_day - timedelta(days=1),
                solar_day,
                solar_day + timedelta(days=1),
            ]
            holidays.append(Holiday("KR", group_days[0], "설날 연휴"))
            holidays.append(Holiday("KR", group_days[1], "설날"))
            holidays.append(Holiday("KR", group_days[2], "설날 연휴"))
            holiday_groups.append(("설날", group_days))

        elif name == "추석":
            group_days = [
                solar_day - timedelta(days=1),
                solar_day,
                solar_day + timedelta(days=1),
            ]
            holidays.append(Holiday("KR", group_days[0], "추석 연휴"))
            holidays.append(Holiday("KR", group_days[1], "추석"))
            holidays.append(Holiday("KR", group_days[2], "추석 연휴"))
            holiday_groups.append(("추석", group_days))

        else:
            holidays.append(Holiday("KR", solar_day, name))

    # 3) 날짜별 보조 자료구조
    holiday_days = [h.day for h in holidays]
    holiday_day_set = set(holiday_days)
    day_counts = Counter(holiday_days)

    substitute_holidays: list[Holiday] = []

    # 4) 단일 휴일 대체공휴일
    for holiday in holidays:
        if holiday.name not in observable_holidays:
            continue

        # 설날/추석은 그룹으로 따로 처리
        if holiday.name in ("설날", "추석", "설날 연휴", "추석 연휴"):
            continue

        has_overlap = day_counts[holiday.day] > 1

        if is_weekend(holiday.day) or has_overlap:
            occupied_days = holiday_day_set | {h.day for h in substitute_holidays}
            sub_day = next_non_holiday(holiday.day, occupied_days)

            already_exists = any(
                h.name == holiday.name and h.note == "대체공휴일"
                for h in substitute_holidays
            )
            if not already_exists:
                substitute_holidays.append(
                    Holiday("KR", sub_day, holiday.name, "대체공휴일")
                )

    # 5) 설날/추석 그룹 대체공휴일
    for group_name, group_days in holiday_groups:
        if group_name not in observable_holidays:
            continue

        has_sunday = any(d.isoweekday() == 7 for d in group_days)
        has_overlap = any(day_counts[d] > 1 for d in group_days)

        if has_sunday or has_overlap:
            occupied_days = holiday_day_set | {h.day for h in substitute_holidays}
            sub_day = next_non_holiday(group_days[-1], occupied_days)

            substitute_holidays.append(
                Holiday("KR", sub_day, group_name, "대체공휴일")
            )

    # 6) 대체공휴일 합치기
    holidays.extend(substitute_holidays)

    # 7) 연 필터
    holidays = [holiday for holiday in holidays if holiday.day.year == year]

    # 8) 월 필터
    if month is not None:
        holidays = [holiday for holiday in holidays if holiday.day.month == month]

    return holidays


def easter_sunday(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def good_friday(year: int) -> date:
    return easter_sunday(year) - timedelta(days=2)


def get_us_holidays(year: int, month: int = None) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "New Year's Day", None, None),
        (6, 19, "Juneteenth National Independence Day", 2021, None),
        (7, 4, "Independence Day", None, None),
        (11, 11, "Veterans Day", None, None),
        (12, 25, "Christmas Day", None, None),
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

    for mm, dd, name, start_year, end_year in fixed_holidays:
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        actual_day = date(year, mm, dd)
        holidays.append(Holiday("US", actual_day, name))

        if actual_day.isoweekday() == 6:
            holidays.append(Holiday("US", actual_day - timedelta(days=1), name, "Observed"))
        elif actual_day.isoweekday() == 7:
            holidays.append(Holiday("US", actual_day + timedelta(days=1), name, "Observed"))

    for mm, n, weekday, name in nth_weekday_holidays:
        if n == -1:
            holiday_day = last_weekday_of_month(year, mm, weekday)
        else:
            holiday_day = nth_weekday_of_month(year, mm, weekday, n)

        holidays.append(Holiday("US", holiday_day, name))

    holidays = [holiday for holiday in holidays if holiday.day.year == year]

    if month is not None:
        holidays = [holiday for holiday in holidays if holiday.day.month == month]

    holidays.sort(key=lambda h: (h.day, h.name, h.note))
    return holidays


def get_us_market_holidays(year: int, month: int = None) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "New Year's Day", None, None),
        (6, 19, "Juneteenth National Independence Day", 2021, None),
        (7, 4, "Independence Day", None, None),
        (12, 25, "Christmas Day", None, None),
    )

    nth_weekday_holidays = (
        (1, 3, 1, "Martin Luther King Jr. Day"),
        (2, 3, 1, "Washington's Birthday"),
        (5, -1, 1, "Memorial Day"),
        (9, 1, 1, "Labor Day"),
        (11, 4, 4, "Thanksgiving Day"),
    )

    holidays = []

    for mm, dd, name, start_year, end_year in fixed_holidays:
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        actual_day = date(year, mm, dd)

        if actual_day.isoweekday() == 6:
            market_day = actual_day - timedelta(days=1)
            holidays.append(Holiday("USM", market_day, name, "Market Holiday (Observed)"))
        elif actual_day.isoweekday() == 7:
            market_day = actual_day + timedelta(days=1)
            holidays.append(Holiday("USM", market_day, name, "Market Holiday (Observed)"))
        else:
            holidays.append(Holiday("USM", actual_day, name, "Market Holiday"))

    for mm, n, weekday, name in nth_weekday_holidays:
        if n == -1:
            holiday_day = last_weekday_of_month(year, mm, weekday)
        else:
            holiday_day = nth_weekday_of_month(year, mm, weekday, n)

        holidays.append(Holiday("USM", holiday_day, name, "Market Holiday"))

    holidays.append(Holiday("USM", good_friday(year), "Good Friday", "Market Holiday"))

    holidays = [holiday for holiday in holidays if holiday.day.year == year]

    if month is not None:
        holidays = [holiday for holiday in holidays if holiday.day.month == month]

    holidays.sort(key=lambda h: (h.day, h.name, h.note))
    return holidays


def get_us_bond_market_holidays(year: int, month: int = None) -> list[Holiday]:
    """
    SIFMA 권고 일정 기반.
    full holiday와 early close를 함께 반환한다.
    Good Friday / 조기종료일은 연도별 데이터 성격이 강하므로 데이터 기반으로 관리한다.
    """
    holidays = []

    # full holidays: 규칙 기반
    fixed_full = (
        (1, 1, "New Year's Day", None, None),
        (6, 19, "Juneteenth", 2021, None),
        (7, 4, "U.S. Independence Day", None, None),
        (11, 11, "Veterans Day", None, None),
        (12, 25, "Christmas Day", None, None),
    )

    nth_weekday_full = (
        (1, 3, 1, "Martin Luther King Day"),
        (2, 3, 1, "Presidents Day"),
        (5, -1, 1, "Memorial Day"),
        (9, 1, 1, "Labor Day"),
        (10, 2, 1, "Columbus Day"),
        (11, 4, 4, "Thanksgiving Day"),
    )

    # 연도별 special full / early close
    special_full = {
        2025: (
            (good_friday(2025), "Good Friday"),
        ),
        2026: (
            # 2026 SIFMA는 Good Friday를 full close가 아니라 12:00 ET early close로 공지
        ),
    }

    early_closes = {
        2025: (
            (date(2024, 12, 31), "New Year's Day 2024/2025", "Early Close 2:00 p.m. ET"),
            (good_friday(2025) - timedelta(days=1), "Good Friday", "Early Close 2:00 p.m. ET"),
            (date(2025, 5, 23), "Memorial Day", "Early Close 2:00 p.m. ET"),
            (date(2025, 7, 3), "U.S. Independence Day", "Early Close 2:00 p.m. ET"),
            (date(2025, 11, 28), "Thanksgiving Day", "Early Close 2:00 p.m. ET"),
            (date(2025, 12, 24), "Christmas Day", "Early Close 2:00 p.m. ET"),
        ),
        2026: (
            (date(2025, 12, 31), "New Year's Day 2025/2026", "Early Close 2:00 p.m. ET"),
            (good_friday(2026), "Good Friday", "Early Close 12:00 p.m. ET"),
            (date(2026, 5, 22), "Memorial Day", "Early Close 2:00 p.m. ET"),
            (date(2026, 7, 2), "U.S. Independence Day (observed)", "Early Close 2:00 p.m. ET"),
            (date(2026, 11, 27), "Thanksgiving Day", "Early Close 2:00 p.m. ET"),
            (date(2026, 12, 24), "Christmas Day", "Early Close 2:00 p.m. ET"),
        ),
    }

    # 1) 규칙 기반 full holiday
    for mm, dd, name, start_year, end_year in fixed_full:
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        actual_day = date(year, mm, dd)

        if actual_day.isoweekday() == 6:
            close_day = actual_day - timedelta(days=1)
        elif actual_day.isoweekday() == 7:
            close_day = actual_day + timedelta(days=1)
        else:
            close_day = actual_day

        holidays.append(Holiday("USB", close_day, name, "Bond Market Holiday"))

    for mm, n, weekday, name in nth_weekday_full:
        if n == -1:
            holiday_day = last_weekday_of_month(year, mm, weekday)
        else:
            holiday_day = nth_weekday_of_month(year, mm, weekday, n)

        holidays.append(Holiday("USB", holiday_day, name, "Bond Market Holiday"))

    # 2) 연도별 special full holiday
    for holiday_day, name in special_full.get(year, ()):
        holidays.append(Holiday("USB", holiday_day, name, "Bond Market Holiday"))

    # 3) 연도별 early close
    for holiday_day, name, note in early_closes.get(year, ()):
        holidays.append(Holiday("USB", holiday_day, name, note))

    holidays = [holiday for holiday in holidays if holiday.day.year == year]

    if month is not None:
        holidays = [holiday for holiday in holidays if holiday.day.month == month]

    holidays.sort(key=lambda h: (h.day, h.name, h.note))
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

    if query.target == "KR":
        holidays.extend(get_kr_holidays(query.year, query.month))
    elif query.target == "US":
        holidays.extend(get_us_holidays(query.year, query.month))
    elif query.target == "USM":
        holidays.extend(get_us_market_holidays(query.year, query.month))
    elif query.target == "USB":
        holidays.extend(get_us_bond_market_holidays(query.year, query.month))
    else:
        holidays.extend(get_kr_holidays(query.year, query.month))
        holidays.extend(get_us_holidays(query.year, query.month))

    holidays.sort(key=lambda h: (h.day, h.country, h.name, h.note))
    return holidays

    