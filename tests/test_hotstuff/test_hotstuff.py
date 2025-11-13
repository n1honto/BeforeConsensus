import unittest
from hotstuff_consensus.hotstuff import HotStuff
from hotstuff_consensus.node import Node
from hotstuff_consensus.block import Block
from core.transaction import Transaction

class TestHotStuff(unittest.TestCase):
    def setUp(self):
        self.nodes = [Node(i, is_leader=(i==0)) for i in range(4)]
        self.hotstuff = HotStuff(self.nodes)

    def test_initial_state(self):
        self.assertEqual(len(self.hotstuff.nodes), 4)
        self.assertEqual(self.hotstuff.current_leader, 0)
        self.assertEqual(len(self.hotstuff.blockchain), 0)

    def test_leader_rotation(self):
        initial_leader = self.hotstuff.current_leader
        new_leader = self.hotstuff.rotate_leader()
        self.assertNotEqual(initial_leader, new_leader)
        self.assertEqual(new_leader, 1)

    def test_propose_block(self):
        tx = Transaction("user1", "user2", 100)
        block = Block(1, [tx], "genesis")
        self.hotstuff.propose_block(block)

        self.assertEqual(len(self.hotstuff.pending_blocks), 1)
        self.assertEqual(self.hotstuff.pending_blocks[0].hash, block.hash)

    def test_commit_block(self):
        tx = Transaction("user1", "user2", 100)
        block = Block(1, [tx], "genesis")
        self.hotstuff.propose_block(block)

        # Симулируем голосование
        for node in self.nodes:
            node.vote(block)

        result = self.hotstuff.commit_block(block)
        self.assertTrue(result)
        self.assertEqual(len(self.hotstuff.blockchain), 1)
        self.assertEqual(self.hotstuff.blockchain[0].hash, block.hash)
        self.assertNotEqual(self.hotstuff.current_leader, 0)  # Лидер должен поменяться

if __name__ == '__main__':
    unittest.main()
