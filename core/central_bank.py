# core/central_bank.py
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import random
from pathlib import Path

# Добавляем корневую директорию в путь поиска модулей
sys.path.append(str(Path(__file__).parent.parent))

from core.utils.helpers import generate_id
from core.utils.exceptions import DigitalRubleError, BankNotFoundError, ValidationError

class CentralBank:
    def __init__(self):
        # Инициализация всех необходимых атрибутов
        self.banks: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.offline_transactions: List[Dict[str, Any]] = []
        self.smart_contracts: Dict[str, Dict[str, Any]] = {}
        self.emission_requests: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.system_status = "operational"
        self.total_emitted = 0
        self.current_balance = 1_000_000_000_000  # 1 трлн рублей

        # Инициализация блокчейна
        self._init_blockchain()

    def _init_blockchain(self):
        """Инициализирует блокчейн"""
        from core.blockchain.blockchain import Blockchain
        self.blockchain = Blockchain()

    def register_bank(self, bank_data: Dict) -> Dict:
        """Регистрирует новый банк"""
        if "name" not in bank_data or "bic" not in bank_data:
            raise ValidationError("Missing required fields", "bank_data")

        bank_id = generate_id("BANK")
        bank = {
            "bank_id": bank_id,
            "name": bank_data["name"],
            "bic": bank_data["bic"],
            "status": "pending",
            "balance": 0.0,
            "registration_date": datetime.now().isoformat()
        }
        self.banks[bank_id] = bank

        # Логируем событие в блокчейне
        self.blockchain.add_transaction(
            sender="SYSTEM",
            recipient=bank_id,
            amount=0,
            transaction_type="bank_registration",
            metadata={"bank_name": bank_data["name"]}
        )

        return {
            "status": "success",
            "bank_id": bank_id,
            "message": "Bank registered successfully"
        }

    def register_user(self, user_type: str) -> Dict:
        """Регистрирует нового пользователя"""
        user_id = generate_id("USER")
        user = {
            "user_id": user_id,
            "user_type": user_type,
            "cash_balance": 10000,
            "digital_wallet_status": "CLOSED",
            "offline_wallet_status": "CLOSED",
            "digital_balance": 0,
            "offline_balance": 0,
            "offline_activation_time": None,
            "offline_deactivation_time": None
        }
        self.users[user_id] = user

        return {
            "status": "success",
            "user_id": user_id,
            "message": "User registered successfully"
        }

    def process_emission(self, bank_id: str, amount: float, purpose: str) -> Dict:
        """Обрабатывает эмиссию цифровых рублей"""
        if bank_id not in self.banks:
            raise BankNotFoundError(bank_id)

        bank = self.banks[bank_id]
        if bank["status"] != "active":
            raise ValidationError("Bank is not active", "bank_status")

        if amount <= 0:
            raise ValidationError("Amount must be positive", "amount")

        # Добавляем транзакцию в блокчейн
        tx_index = self.blockchain.add_transaction(
            sender="CENTRAL_BANK",
            recipient=bank_id,
            amount=amount,
            transaction_type="emission",
            metadata={"purpose": purpose}
        )

        # Майним блок
        self.blockchain.mine_block()

        # Обновляем балансы
        bank["balance"] += amount
        self.current_balance -= amount
        self.total_emitted += amount

        return {
            "status": "success",
            "transaction_id": f"TX{tx_index}",
            "new_balance": bank["balance"],
            "message": "Emission processed successfully"
        }

    def get_all_users(self) -> List[Dict]:
        """Возвращает список всех пользователей"""
        return list(self.users.values())

    def get_all_banks(self) -> List[Dict]:
        """Возвращает список всех банков"""
        return list(self.banks.values())

    def get_transaction_history(self) -> List[Dict]:
        """Возвращает историю транзакций"""
        return self.transactions.copy()
