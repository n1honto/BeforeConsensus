# hotstuff_consensus/node.py
from typing import Dict, Any, Optional
from .hotstuff import HotStuffConsensus

class HotStuffNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.consensus = HotStuffConsensus(node_id)
        self.received_blocks: Dict[str, Dict] = {}  # block_hash: Block

    def receive_proposal(self, proposal: Dict) -> Dict:
        """Получает предложение блока от лидера"""
        self.received_blocks[proposal["block"]["hash"]] = proposal["block"]
        return {
            "status": "success",
            "message": "Block proposal received",
            "block_hash": proposal["block"]["hash"]
        }

    def receive_vote(self, voter_id: str, block_hash: str) -> Dict:
        """Получает голос от другого узла"""
        if block_hash not in self.received_blocks:
            return {"status": "error", "message": "Unknown block"}

        return self.consensus.vote(block_hash, voter_id)

    def propose_block(self, block_data: Dict) -> Dict:
        """Предлагает новый блок (если этот узел - лидер)"""
        return self.consensus.propose(block_data)

    def vote_for_block(self, block_hash: str) -> Dict:
        """Голосует за блок"""
        return self.consensus.vote(block_hash, self.node_id)

    def new_view(self, new_view: int) -> Dict:
        """Инициирует переход к новому виду"""
        return self.consensus.new_view(new_view)

    def get_status(self) -> Dict:
        """Возвращает статус узла"""
        return {
            **self.consensus.get_status(),
            "node_id": self.node_id,
            "received_blocks": len(self.received_blocks)
        }
