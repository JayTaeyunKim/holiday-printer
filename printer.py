from models import Holiday, Query
import pandas as pd
import os


def print_holidays(holidays: list[Holiday]) -> None:

    if len(holidays) == 0:
        print("해당 조건의 휴일이 없습니다.")
        return

    for holiday in holidays:
        if holiday.note:
            print(f"[{holiday.country}] {holiday.day} {holiday.name} ({holiday.note})")
        else:
            print(f"[{holiday.country}] {holiday.day} {holiday.name}")

def print_to_csv(holidays: list[Holiday], query: Query) -> None:
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
    
    holidays_df = pd.DataFrame({"국가":country, "날짜": day, "휴일명": name, "비고": note})

    base_dir = os.getcwd()
    folder_path = os.path.join(base_dir, '휴일리스트')
    os.makedirs(folder_path, exist_ok=True)

    try:
        if query.target is None:
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
        holidays_df.to_excel(file_path, index=False, engine='openpyxl')
    except:
        print("에러 발생, 저장 불가\n")
    else:
        print(filename + " 저장 완료\n")

