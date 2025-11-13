import unittest
from core.user import User
from core.wallet import Wallet
from core.transaction import Transaction
from hotstuff_consensus.hotstuff import HotStuff
from hotstuff_consensus.node import Node
from hotstuff_consensus.block import Block

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Создаём пользователей
        self.user1 = User("user1", "individual")
        self.user2 = User("user2", "individual")

        # Создаём кошельки
        self.user1.wallet = Wallet("user1")
        self.user2.wallet = Wallet("user2")

        # Пополняем кошельки
        self.user1.wallet.add_funds(1000)
        self.user2.wallet.add_funds(1000)

        # Создаём узлы HotStuff
        self.nodes = [Node(i, is_leader=(i==0)) for i in range(4)]
        self.hotstuff = HotStuff(self.nodes)

    def test_offline_transaction_flow(self):
        # Создаём транзакцию
        tx = Transaction("user1", "user2", 100)
        tx.mark_as_offline()

        # Добавляем транзакцию в кошелёк
        result = self.user1.wallet.add_offline_transaction(tx)
        self.assertTrue(result)

        # Проверяем балансы
        self.assertEqual(self.user1.wallet.get_balance(), 900)
        self.assertEqual(len(self.user1.wallet.pending_transactions), 1)

        # Создаём блок с транзакцией
        block = Block(1, [tx], "genesis")

        # Проходим консенсус
        self.hotstuff.propose_block(block)
        for node in self.nodes:
            node.vote(block)

        # Подтверждаем блок
        result = self.hotstuff.commit_block(block)
        self.assertTrue(result)

        # Подтверждаем транзакцию в кошельках
        self.user1.wallet.confirm_transaction(tx.id, block.hash)
        self.user2.wallet.confirm_transaction(tx.id, block.hash)

        # Проверяем историю транзакций
        history1 = self.user1.wallet.get_transaction_history()
        history2 = self.user2.wallet.get_transaction_history()

        self.assertEqual(len(history1), 2)  # Пополнение + транзакция
        self.assertEqual(len(history2), 2)  # Пополнение + транзакция

        # Проверяем, что транзакция подтверждена
        tx_info = [t for t in history1 if t['type'] == 'offline_transaction'][0]
        self.assertEqual(tx_info['status'], 'confirmed')
        self.assertEqual(tx_info['block_hash'], block.hash)

if __name__ == '__main__':
    unittest.main()
