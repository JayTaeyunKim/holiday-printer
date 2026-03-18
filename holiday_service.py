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

    lunar_holidays = (
        (1, 1, "설날"),      # 앞뒤로 1일씩 휴일
        (4, 8, "부처님오신날"),
        (8, 15, "추석"),     # 앞뒤로 1일씩 휴일
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
    for mm, dd, name in fixed_holidays:
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

    # 3) 날짜별 공휴일 개수 / 이름 맵
    holiday_days = [h.day for h in holidays]
    holiday_day_set = set(holiday_days)
    day_counts = Counter(holiday_days)

    holiday_name_map: dict[date, list[str]] = {}
    for h in holidays:
        holiday_name_map.setdefault(h.day, []).append(h.name)

    substitute_holidays: list[Holiday] = []

    # 4) 단일 휴일 대체공휴일
    for holiday in holidays:
        if holiday.name not in observable_holidays:
            continue

        # 설날/추석은 그룹으로 따로 처리하므로 여기서는 제외
        if holiday.name in ("설날", "추석"):
            continue

        # 연휴 이름도 단일 휴일 처리 대상에서 제외
        if holiday.name in ("설날 연휴", "추석 연휴"):
            continue

        has_overlap = day_counts[holiday.day] > 1

        if is_weekend(holiday.day) or has_overlap:
            occupied_days = holiday_day_set | {h.day for h in substitute_holidays}
            sub_day = next_non_holiday(holiday.day, occupied_days)

            # 같은 이름의 대체공휴일 중복 생성 방지
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

    # 9) 정렬
    holidays.sort(key=lambda h: (h.day, h.name, h.note))

    return holidays


def get_us_holidays(year: int, month: int = None) -> list[Holiday]:
    fixed_holidays = (
        (1, 1, "New Year's Day"),
        (6, 19, "Juneteenth National Independence Day"),
        (7, 4, "Independence Day"),
        (11, 11, "Veterans Day"),
        (12, 25, "Christmas Day"),
    )

    nth_weekday_holidays = ( # (월, n, 요일(월:1~일:7)) : n이 -1은 마지막을 의미
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

    