import uuid
from datetime import datetime

class FinancialOrganization:
    def __init__(self, name: str, central_bank):
        self.name = name
        self.cash_balance = 1000000  # Начальный баланс безналичных рублей
        self.digital_balance = 0
        self.central_bank = central_bank
        self.transactions = []
        self.central_bank.register_bank(self.name)

    def request_emission(self, amount: int) -> bool:
        if amount <= 0:
            print(f"❌ [Банк {self.name}] Сумма эмиссии должна быть положительной.")
            return False

        if self.cash_balance < amount:
            print(f"❌ [Банк {self.name}] Недостаточно безналичных рублей для эмиссии.")
            return False

        if self.central_bank.issue_currency(self.name, amount):
            self.cash_balance -= amount
            self.digital_balance += amount
            print(f"💰 [Банк {self.name}] Эмиссия выполнена. Сумма: {amount} ЦР.")
            return True
        return False

    def exchange_cash_to_digital(self, user_id: str, amount: int) -> bool:
        if amount <= 0:
            print(f"❌ [Банк {self.name}] Сумма обмена должна быть положительной.")
            return False

        if self.digital_balance < amount:
            print(f"❌ [Банк {self.name}] Недостаточно цифровых рублей для обмена.")
            return False

        self.cash_balance += amount
        self.digital_balance -= amount
        print(f"💱 [Банк {self.name}] Обмен безналичных рублей на цифровые для пользователя {user_id}. Сумма: {amount} ЦР.")
        return True

    def add_transaction_to_queue(self, transaction):
        self.transactions.append(transaction)
        self.central_bank.add_transaction_to_queue(transaction)

    def create_transaction(self, sender_id: str, recipient_id: str, amount: int):
        transaction = {
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "timestamp": datetime.now(),
            "status": "pending",
            "bank": self.name
        }
        self.add_transaction_to_queue(transaction)
        return transaction
