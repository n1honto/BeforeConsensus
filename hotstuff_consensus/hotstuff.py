from typing import List
from .block import Block
from .node import Node

class HotStuff:
    def __init__(self, nodes: List[Node] = None):
        self.nodes = nodes or []
        self.current_leader = 0
        self.blockchain: List[Block] = []
        self.pending_blocks: List[Block] = []

    def add_node(self, node: Node) -> None:
        """Добавляет узел в сеть"""
        self.nodes.append(node)

    def rotate_leader(self) -> int:
        """Ротирует лидера"""
        self.nodes[self.current_leader].become_follower()
        self.current_leader = (self.current_leader + 1) % len(self.nodes)
        self.nodes[self.current_leader].become_leader()
        return self.current_leader

    def propose_block(self, block: Block) -> None:
        """Предлагает новый блок"""
        self.pending_blocks.append(block)
        for node in self.nodes:
            node.receive_proposal(block)

    def get_votes(self, block: Block) -> int:
        """Собирает голоса за блок"""
        return sum(1 for node in self.nodes if node.vote(block))

    def commit_block(self, block: Block) -> bool:
        """Подтверждает блок и добавляет его в цепочку"""
        if block.hash in [b.hash for b in self.blockchain]:
            return False

        self.blockchain.append(block)
        self.rotate_leader()
        return True
