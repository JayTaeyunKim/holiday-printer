from models import Holiday, Query
import pandas as pd
import os
from datetime import date, timedelta


class HolidayPrinter:
    def __init__(self):
        self.history = {}


    def print_holidays(self, holidays: list[Holiday]) -> None:
        if len(holidays) == 0:
            print("해당 조건의 휴일이 없습니다.")
            return

        for holiday in holidays:
            if holiday.note:
                print(f"[{holiday.country}] {holiday.day} {holiday.name} ({holiday.note})")
            else:
                print(f"[{holiday.country}] {holiday.day} {holiday.name}")


    def save_to_excel(self, holidays: list[Holiday], query: Query | None = None) -> None:
        if len(holidays) == 0:
            print("해당 조건의 휴일이 없습니다.")
            return

        country = []
        day = []
        name = []
        note = []

        for holiday in holidays:
            country.append(holiday.country)
            day.append(holiday.day)
            name.append(holiday.name)
            note.append(holiday.note)

        holidays_df = pd.DataFrame({
            "국가": country,
            "날짜": day,
            "휴일명": name,
            "비고": note
        })

        base_dir = os.getcwd()
        folder_path = os.path.join(base_dir, "휴일리스트")
        os.makedirs(folder_path, exist_ok=True)

        try:
            if query is None:
                years = sorted({h.day.year for h in holidays})
                filename = f"{years[0]}_{years[-1]}_휴일.xlsx"
            elif query.target is None:
                if query.month is None:
                    filename = f"{query.year}.xlsx"
                else:
                    filename = f"{query.year}_{query.month}.xlsx"
            else:
                if query.month is None:
                    filename = f"{query.target}_{query.year}.xlsx"
                else:
                    filename = f"{query.target}_{query.year}_{query.month}.xlsx"

            file_path = os.path.join(folder_path, filename)
            holidays_df.to_excel(file_path, index=False, engine="openpyxl")

        except Exception as e:
            print(f"에러 발생, 저장 불가: {e}\n")
        else:
            print(filename + " 저장 완료\n")


    def make_history(self, holidays: list[Holiday], query: Query) -> None:
        try:
            if query.target is None:
                if query.month is None:
                    key = f"{query.year}"
                else:
                    key = f"{query.year}_{query.month}"
            else:
                if query.month is None:
                    key = f"{query.target}_{query.year}"
                else:
                    key = f"{query.target}_{query.year}_{query.month}"

            if key not in self.history:
                self.history[key] = holidays

        except Exception as e:
            print(f"에러 발생, 히스토리 저장 불가: {e}\n")


    def save_history_to_excel(self) -> None:
        holidays = []

        for key in self.history:
            holidays.extend(self.history[key])

        holidays.sort(key=lambda h: (h.day, h.country, h.name, h.note))

        self.save_to_excel(holidays)
    

    def get_business_days_from_history(self) -> list[date]:
        if not self.history:
            return []

        all_holidays = []
        for key in self.history:
            all_holidays.extend(self.history[key])

        if not all_holidays:
            return []

        holiday_days = {holiday.day for holiday in all_holidays}

        min_year = min(holiday.day.year for holiday in all_holidays)
        max_year = max(holiday.day.year for holiday in all_holidays)

        start_day = date(min_year, 1, 1)
        end_day = date(max_year, 12, 31)

        while start_day.isoweekday() >= 6 or start_day in holiday_days:
            start_day += timedelta(days=1)

        while end_day.isoweekday() >= 6 or end_day in holiday_days:
            end_day -= timedelta(days=1)

        business_days = []
        current_day = start_day

        while current_day <= end_day:
            if current_day.isoweekday() < 6 and current_day not in holiday_days:
                business_days.append(current_day)
            current_day += timedelta(days=1)

        return business_days


    def save_business_days_to_excel(self) -> None:
        business_days = self.get_business_days_from_history()

        if not business_days:
            print("저장할 영업일이 없습니다.")
            return

        min_year = business_days[0].year
        max_year = business_days[-1].year

        business_days_df = pd.DataFrame({
            "영업일": business_days
        })

        base_dir = os.getcwd()
        folder_path = os.path.join(base_dir, "휴일리스트")
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{min_year}_{max_year}_영업일.xlsx"
        file_path = os.path.join(folder_path, filename)

        try:
            business_days_df.to_excel(file_path, index=False, engine="openpyxl")
        except Exception as e:
            print(f"에러 발생, 저장 불가: {e}\n")
        else:
            print(filename + " 저장 완료\n")


    def print_business_days_from_history(self) -> None:
        business_days = self.get_business_days_from_history()

        if not business_days:
            print("출력할 영업일이 없습니다.")
            return

        for business_day in business_days:
            print(business_day)