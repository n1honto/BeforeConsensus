# hotstuff_consensus/hotstuff.py
import json
import time
from typing import Dict, List, Set, Optional, Any

class HotStuffConsensus:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.view = 0
        self.leader = None
        self.quorum = 0
        self.nodes: Set[str] = set()
        self.proposed_block: Optional[Dict] = None
        self.locked_block: Optional[Dict] = None
        self.votes: Dict[str, Set[str]] = {}  # block_hash: set(node_ids)
        self.new_view_votes: Set[str] = set()

    def add_node(self, node_id: str):
        """Добавляет узел в сеть консенсуса"""
        self.nodes.add(node_id)
        self.quorum = (len(self.nodes) * 2) // 3 + 1  # 2f+1 византийская устойчивость

    def set_leader(self, leader_id: str):
        """Устанавливает лидера для текущего вида"""
        self.leader = leader_id

    def propose(self, block: Dict) -> Dict:
        """Предлагает новый блок (вызывается лидером)"""
        if self.node_id != self.leader:
            return {"status": "error", "message": "Only leader can propose blocks"}

        self.proposed_block = block
        self.votes[block["hash"]] = set()

        return {
            "status": "success",
            "block": block,
            "view": self.view,
            "leader": self.leader
        }

    def vote(self, block_hash: str, voter_id: str) -> Dict:
        """Голосует за блок"""
        if block_hash not in self.votes:
            return {"status": "error", "message": "Unknown block"}

        self.votes[block_hash].add(voter_id)

        # Проверяем кворум
        if len(self.votes[block_hash]) >= self.quorum:
            # Блок принят
            return {
                "status": "success",
                "message": "Block accepted by quorum",
                "block_hash": block_hash,
                "votes": list(self.votes[block_hash])
            }

        return {
            "status": "pending",
            "message": "Vote recorded, waiting for quorum",
            "current_votes": len(self.votes[block_hash]),
            "required": self.quorum
        }

    def new_view(self, new_view: int) -> Dict:
        """Переход к новому виду"""
        if new_view <= self.view:
            return {"status": "error", "message": "New view must be greater than current"}

        self.new_view_votes.add(self.node_id)

        if len(self.new_view_votes) >= self.quorum:
            self.view = new_view
            self.leader = list(self.nodes)[self.view % len(self.nodes)]
            self.new_view_votes = set()
            self.votes = {}

            return {
                "status": "success",
                "message": "View changed successfully",
                "new_view": self.view,
                "new_leader": self.leader
            }

        return {
            "status": "pending",
            "message": "New view vote recorded",
            "current_votes": len(self.new_view_votes),
            "required": self.quorum
        }

    def get_status(self) -> Dict:
        """Возвращает текущий статус консенсуса"""
        return {
            "view": self.view,
            "leader": self.leader,
            "nodes": list(self.nodes),
            "quorum": self.quorum,
            "proposed_block": self.proposed_block,
            "locked_block": self.locked_block,
            "votes": {k: list(v) for k, v in self.votes.items()}
        }
