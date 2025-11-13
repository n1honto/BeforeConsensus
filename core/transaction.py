import uuid
from datetime import datetime
import hashlib

class Transaction:
    def __init__(self, sender_id: str, recipient_id: str, amount: int):
        self.id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.timestamp = datetime.now()
        self.status = "pending"
        self.signature = None
        self.is_offline = False

    def sign(self, private_key: str):
        transaction_data = f"{self.sender_id}{self.recipient_id}{self.amount}{self.timestamp}"
        self.signature = hashlib.sha256((transaction_data + private_key).encode()).hexdigest()

    def verify_signature(self, public_key: str) -> bool:
        transaction_data = f"{self.sender_id}{self.recipient_id}{self.amount}{self.timestamp}"
        expected_signature = hashlib.sha256((transaction_data + public_key).encode()).hexdigest()
        return self.signature == expected_signature

    def mark_as_offline(self):
        self.is_offline = True
        self.status = "offline"
