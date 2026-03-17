'''
휴일 유형
1. 고정일 유형
2. N번째 요일 휴일
3. 마지막 요일 휴일
4. 한국 음력 휴일
'''

#models.py → parser.py → holiday_service.py(고정휴일만) → printer.py → main.py → 테스트 → 기능 확장

from parser import parse_input
from holiday_service import get_holidays_by_query
from printer import print_holidays

def main() -> None:
    text = input("입력 예시: 2026 / KR 2026 / US 2026 05\n입력: ")

    try:
        query = parse_input(text)
        holidays = get_holidays_by_query(query)
        print_holidays(holidays)
    except ValueError as e:
        print(f"입력 오류: {e}")

if __name__ == '__main__':
    main()



