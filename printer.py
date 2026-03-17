from models import Holiday


def print_holidays(holidays: list[Holiday]) -> None:

    if len(holidays) == 0:
        print("해당 조건의 휴일이 없습니다.")
        return

    for holiday in holidays:
        if holiday.note:
            print(f"[{holiday.country}] {holiday.day} {holiday.name} ({holiday.note})")
        else:
            print(f"[{holiday.country}] {holiday.day} {holiday.name}")