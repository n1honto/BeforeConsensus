import unittest
from hotstuff_consensus.node import Node
from hotstuff_consensus.block import Block
from core.transaction import Transaction

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node = Node(0, is_leader=True)
        self.tx = Transaction("user1", "user2", 100)
        self.block = Block(1, [self.tx], "genesis")

    def test_node_creation(self):
        self.assertEqual(self.node.node_id, 0)
        self.assertTrue(self.node.is_leader)
        self.assertIsNone(self.node.current_block)

    def test_receive_proposal(self):
        self.node.receive_proposal(self.block)
        self.assertEqual(self.node.current_block.hash, self.block.hash)

    def test_vote(self):
        self.node.receive_proposal(self.block)
        result = self.node.vote(self.block)
        self.assertTrue(result)

        # Проверка повторного голосования
        result = self.node.vote(self.block)
        self.assertFalse(result)

    def test_leader_change(self):
        self.node.become_follower()
        self.assertFalse(self.node.is_leader)

        self.node.become_leader()
        self.assertTrue(self.node.is_leader)

if __name__ == '__main__':
    unittest.main()
