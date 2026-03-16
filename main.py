'''
휴일 유형
1. 고정일 유형
2. N번째 요일 휴일
3. 마지막 요일 휴일
4. 한국 음력 휴일
'''

#models.py → parser.py → holiday_service.py(고정휴일만) → printer.py → main.py → 테스트 → 기능 확장

from dataclasses import dataclass
from typing import Optional

