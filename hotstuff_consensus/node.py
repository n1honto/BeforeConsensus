from typing import Optional
from .block import Block

class Node:
    def __init__(self, node_id: int, is_leader: bool = False):
        self.node_id = node_id
        self.is_leader = is_leader
        self.current_block: Optional[Block] = None
        self.voted = False

    def receive_proposal(self, block: Block) -> None:
        """Получает предложение блока"""
        self.current_block = block
        self.voted = False

    def vote(self, block: Block) -> bool:
        """Голосует за блок (1 - за, 0 - против)"""
        if self.current_block.hash != block.hash:
            return False

        if self.voted:
            return False

        self.voted = True
        return True  # Всегда голосуем "за" в этой упрощённой версии

    def become_leader(self) -> None:
        """Делает узел лидером"""
        self.is_leader = True

    def become_follower(self) -> None:
        """Делает узел последователем"""
        self.is_leader = False
