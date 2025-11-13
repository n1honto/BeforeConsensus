import unittest
from datetime import datetime
from hotstuff_consensus.block import Block
from core.transaction import Transaction

class TestBlock(unittest.TestCase):
    def test_block_creation(self):
        tx1 = Transaction("user1", "user2", 100)
        tx2 = Transaction("user2", "user3", 200)
        block = Block(1, [tx1, tx2], "genesis")

        self.assertEqual(block.height, 1)
        self.assertEqual(len(block.transactions), 2)
        self.assertEqual(block.parent_hash, "genesis")
        self.assertIsInstance(block.timestamp, datetime)
        self.assertIsNotNone(block.hash)

    def test_block_hash(self):
        tx = Transaction("user1", "user2", 100)
        block1 = Block(1, [tx], "genesis")
        block2 = Block(1, [tx], "genesis")

        self.assertEqual(block1.hash, block2.hash)

    def test_block_to_dict(self):
        tx = Transaction("user1", "user2", 100)
        block = Block(1, [tx], "genesis")
        block_dict = block.to_dict()

        self.assertEqual(block_dict['height'], 1)
        self.assertEqual(len(block_dict['transactions']), 1)
        self.assertEqual(block_dict['parent_hash'], "genesis")
        self.assertEqual(block_dict['hash'], block.hash)

if __name__ == '__main__':
    unittest.main()
