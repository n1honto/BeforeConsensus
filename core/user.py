from core.wallet import Wallet

class User:
    def __init__(self, user_id: str, user_type: str):
        self.user_id = user_id
        self.user_type = user_type
        self.has_digital_wallet = False
        self.cash_balance = 10000.0
        self.digital_balance = 0.0
        self.wallet = None
