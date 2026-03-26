from models import Query


VALID_TARGETS = {"KR", "US", "USM", "USB", "USS"}


def parse_input(text: str) -> Query:
    input_parts = text.strip().split()

    if len(input_parts) == 1:
        year_text = input_parts[0]

        if not year_text.isdigit():
            raise ValueError("연도는 숫자로 입력해야 합니다.")

        return Query(target=None, year=int(year_text))

    elif len(input_parts) == 2:
        first = input_parts[0].upper()
        second = input_parts[1]

        if first in VALID_TARGETS:
            if not second.isdigit():
                raise ValueError("연도는 숫자로 입력해야 합니다.")
            return Query(target=first, year=int(second))

        if not input_parts[0].isdigit():
            raise ValueError("연도는 숫자로 입력해야 합니다.")
        if not input_parts[1].isdigit():
            raise ValueError("월은 숫자로 입력해야 합니다.")

        year = int(input_parts[0])
        month = int(input_parts[1])

        if not 1 <= month <= 12:
            raise ValueError("월은 1~12 사이여야 합니다.")

        return Query(target=None, year=year, month=month)

    elif len(input_parts) == 3:
        target = input_parts[0].upper()
        year_text = input_parts[1]
        month_text = input_parts[2]

        if target not in VALID_TARGETS:
            raise ValueError("대상은 KR, US, USM, USB, USS 중 하나여야 합니다.")
        if not year_text.isdigit():
            raise ValueError("연도는 숫자로 입력해야 합니다.")
        if not month_text.isdigit():
            raise ValueError("월은 숫자로 입력해야 합니다.")

        year = int(year_text)
        month = int(month_text)

        if not 1 <= month <= 12:
            raise ValueError("월은 1~12 사이여야 합니다.")

        return Query(target=target, year=year, month=month)

    else:
        raise ValueError("입력 형식이 올바르지 않습니다.")