import unittest
from core.transaction import Transaction

class TestTransaction(unittest.TestCase):
    def test_sign_and_verify(self):
        transaction = Transaction("user1", "user2", 100)
        transaction.sign("private_key")
        self.assertTrue(transaction.verify_signature("private_key"))
