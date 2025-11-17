# core/utils/helpers.py
import random
import string
from datetime import datetime
import json

def generate_id(prefix: str = "", length: int = 6) -> str:
    """Генерирует уникальный идентификатор"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{timestamp}{random_part}" if prefix else f"{timestamp}{random_part}"
