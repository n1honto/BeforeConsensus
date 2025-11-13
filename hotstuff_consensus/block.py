import hashlib
import json
from datetime import datetime
from typing import List, Any

class Block:
    def __init__(self, height: int, transactions: List[Any], parent_hash: str = ""):
        self.height = height
        self.transactions = transactions
        self.parent_hash = parent_hash
        self.timestamp = datetime.now()
        self._hash = None

    @property
    def hash(self) -> str:
        if self._hash is None:
            block_data = {
                "height": self.height,
                "transactions": [tx.id for tx in self.transactions],
                "parent_hash": self.parent_hash,
                "timestamp": str(self.timestamp)
            }
            self._hash = hashlib.sha256(
                json.dumps(block_data, sort_keys=True).encode()
            ).hexdigest()
        return self._hash

    def to_dict(self) -> dict:
        return {
            "height": self.height,
            "transactions": [tx.id for tx in self.transactions],
            "parent_hash": self.parent_hash,
            "timestamp": str(self.timestamp),
            "hash": self.hash
        }
