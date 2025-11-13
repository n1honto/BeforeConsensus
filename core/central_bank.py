import uuid
from datetime import datetime
from typing import Dict, List

class CentralBank:
    def __init__(self):
        self.total_balance = 0
        self.transaction_queue = []
        self.banks = {}

    def register_bank(self, bank_name: str) -> None:
        if bank_name not in self.banks:
            self.banks[bank_name] = {"status": "active"}
            print(f"🔹 [ЦБ] Банк {bank_name} успешно зарегистрирован в системе.")
        else:
            print(f"⚠️ [ЦБ] Банк {bank_name} уже зарегистрирован.")

    def issue_currency(self, bank_name: str, amount: int) -> bool:
        if bank_name not in self.banks:
            print(f"❌ [ЦБ] Банк {bank_name} не зарегистрирован.")
            return False

        self.total_balance += amount
        print(f"💰 [ЦБ] Эмиссия выполнена для банка {bank_name}. Сумма: {amount} ЦР.")
        return True

    def add_transaction_to_queue(self, transaction) -> None:
        if hasattr(transaction, 'is_offline') and transaction.is_offline:
            print(f"📥 [ЦБ] Оффлайн-транзакция {transaction.id} добавлена в очередь.")
        else:
            print(f"📥 [ЦБ] Транзакция {transaction.id} добавлена в очередь.")
        self.transaction_queue.append(transaction)
