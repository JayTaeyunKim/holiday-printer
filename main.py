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
from printer import print_holidays, print_to_csv


def main() -> None:
    while True:
        text = input("입력 예시: 2026 / KR 2026 / US 2026 05 / USM 2026\n입력: ")

        if text == '-1':
            break

        try:
            query = parse_input(text)
            holidays = get_holidays_by_query(query)
            print_holidays(holidays)
        except ValueError as e:
            print(f"입력 오류: {e}")
        
        save_or_not = input("엑셀로 저장하시겠습니까? y/n: ")
        if save_or_not.lower() == "y":
            print_to_csv(holidays, query)
        else:
            print()

if __name__ == '__main__':
    main()



