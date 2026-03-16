from models import Query


def parse_input(text: str) -> Query:
    input_parts = text.strip().split()

    if len(input_parts) == 1:
        if not input_parts[0].isdigit():
            raise ValueError("연도는 숫자로 입력해야 합니다.")
        return Query(country=None, year=int(input_parts[0]))

    elif len(input_parts) == 2:
        first = input_parts[0].upper()
        second = input_parts[1]

        if first == "KR" or first == "US":
            if not second.isdigit():
                raise ValueError("연도는 숫자로 입력해야 합니다.")
            return Query(country=first, year=int(second))
        else:
            if not input_parts[0].isdigit():
                raise ValueError("연도는 숫자로 입력해야 합니다.")
            if not input_parts[1].isdigit():
                raise ValueError("월은 숫자로 입력해야 합니다.")

            year = int(input_parts[0])
            month = int(input_parts[1])

            if month < 1 or month > 12:
                raise ValueError("월은 1~12 사이여야 합니다.")

            return Query(country=None, year=year, month=month)

    elif len(input_parts) == 3:
        country = input_parts[0].upper()
        year_text = input_parts[1]
        month_text = input_parts[2]

        if country not in ("KR", "US"):
            raise ValueError("국가는 KR 또는 US만 입력할 수 있습니다.")
        if not year_text.isdigit():
            raise ValueError("연도는 숫자로 입력해야 합니다.")
        if not month_text.isdigit():
            raise ValueError("월은 숫자로 입력해야 합니다.")

        year = int(year_text)
        month = int(month_text)

        if month < 1 or month > 12:
            raise ValueError("월은 1~12 사이여야 합니다.")

        return Query(country=country, year=year, month=month)

    else:
        raise ValueError("입력 형식이 올바르지 않습니다.")