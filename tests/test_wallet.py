import unittest
from core.wallet import Wallet
from core.transaction import Transaction

class TestWallet(unittest.TestCase):
    def test_add_offline_transaction(self):
        wallet = Wallet(1000)
        transaction = Transaction("user1", "user2", 100)
        wallet.add_offline_transaction(transaction)
        self.assertEqual(len(wallet.pending_offline_transactions), 1)
