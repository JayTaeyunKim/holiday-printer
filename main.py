'''
휴일 유형
1. 고정일 유형
2. N번째 요일 휴일
3. 마지막 요일 휴일
4. 한국 음력 휴일
5. 한국 대체공휴일
6. 한국 임시공휴일
'''

from parser import parse_input
from holiday_service import get_holidays_by_query
# from printer import print_holidays, print_to_csv
from printer import HolidayPrinter

def main() -> None:

    printer = HolidayPrinter()

    while True:
        text = input("입력 예시: 2026 / KR 2026 / US 2026 05 / USM 2026 / USB 2026 / USS 2026 11\n입력: ")

        if text == '-1':
            break

        try:
            query = parse_input(text)
            holidays = get_holidays_by_query(query)
            printer.make_history(holidays, query)
            printer.print_holidays(holidays)
        except ValueError as e:
            print(f"입력 오류: {e}")
        
        save_or_not = input("엑셀로 저장하시겠습니까? y/n/all: ")
        if save_or_not.lower() == "y":
            printer.print_to_csv(holidays, query)

        elif save_or_not == "all":
            printer.save_history_to_excel()
            printer.save_business_days_to_excel()
        else:
            print()


if __name__ == '__main__':
    main()



