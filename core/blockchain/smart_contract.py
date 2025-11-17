# core/blockchain/smart_contract.py
import json
import hashlib
from typing import Dict, Any, List, Optional

class SmartContract:
    def __init__(self, contract_id: str, code: str, creator: str):
        self.contract_id = contract_id
        self.code = code
        self.creator = creator
        self.storage: Dict[str, Any] = {}
        self.events: List[Dict] = []

    def compute_hash(self) -> str:
        """Вычисляет хэш контракта"""
        contract_string = json.dumps({
            "contract_id": self.contract_id,
            "code": self.code,
            "creator": self.creator,
            "storage": self.storage
        }, sort_keys=True).encode()
        return hashlib.sha256(contract_string).hexdigest()

    def execute(self, method: str, args: List[Any], context: Dict) -> Any:
        """Выполняет метод смарт-контракта"""
        # В реальной системе здесь был бы интерпретатор кода контракта
        # Для упрощения используем заранее определенные методы

        if method == "get_balance":
            return self._get_balance(args, context)
        elif method == "transfer":
            return self._transfer(args, context)
        elif method == "emit_event":
            return self._emit_event(args, context)
        else:
            raise ValueError(f"Method {method} not found in contract")

    def _get_balance(self, args: List[Any], context: Dict) -> float:
        """Возвращает баланс аккаунта"""
        account = args[0]
        return self.storage.get("balances", {}).get(account, 0.0)

    def _transfer(self, args: List[Any], context: Dict) -> bool:
        """Выполняет перевод средств"""
        from_account, to_account, amount = args

        if from_account not in self.storage.setdefault("balances", {}):
            self.storage["balances"][from_account] = 0.0

        if to_account not in self.storage["balances"]:
            self.storage["balances"][to_account] = 0.0

        if self.storage["balances"][from_account] < amount:
            return False

        self.storage["balances"][from_account] -= amount
        self.storage["balances"][to_account] += amount

        # Логируем событие
        self.events.append({
            "type": "transfer",
            "from": from_account,
            "to": to_account,
            "amount": amount,
            "timestamp": context["timestamp"]
        })

        return True

    def _emit_event(self, args: List[Any], context: Dict) -> Dict:
        """Эмитирует событие"""
        event_type, data = args
        event = {
            "type": event_type,
            "data": data,
            "timestamp": context["timestamp"],
            "contract": self.contract_id
        }
        self.events.append(event)
        return event

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует контракт в словарь"""
        return {
            "contract_id": self.contract_id,
            "code_hash": self.compute_hash(),
            "creator": self.creator,
            "storage": self.storage,
            "events": self.events
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SmartContract':
        """Создает контракт из словаря"""
        contract = cls(
            contract_id=data["contract_id"],
            code=data.get("code", ""),
            creator=data["creator"]
        )
        contract.storage = data.get("storage", {})
        contract.events = data.get("events", [])
        return contract
