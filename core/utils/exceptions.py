# core/utils/exceptions.py
class DigitalRubleError(Exception):
    """Базовое исключение для системы цифрового рубля"""
    pass

class BankNotFoundError(DigitalRubleError):
    """Банк не найден"""
    def __init__(self, bank_id: str):
        super().__init__(f"Bank with ID {bank_id} not found")

class ValidationError(DigitalRubleError):
    """Ошибка валидации"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(f"Validation failed{(f' for {field}' if field else '')}: {message}")

class LimitExceededError(DigitalRubleError):
    """Превышен лимит"""
    def __init__(self, limit_type: str, limit: float, requested: float):
        super().__init__(
            f"{limit_type} limit exceeded. Limit: {limit}, Requested: {requested}"
        )

class ComplianceError(DigitalRubleError):
    """Ошибка комплаенса"""
    def __init__(self, message: str, check_type: str = None):
        super().__init__(
            f"Compliance check failed{(f' [{check_type}]' if check_type else '')}: {message}"
        )
