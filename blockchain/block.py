from dataclasses import dataclass
from typing import Any

@dataclass
class Block:
    """
    Centralized Private Blockchain Block representing a transaction.
    
    Structure:
    - txn_id: Transaction ID (SHA-3 Hash of UID, FID, Timestamp, Amount)
    - prev_hash: Previous Block Hash
    - timestamp: Timestamp of the transaction
    - dispute_or_refund_flag: Boolean flag to handle failed charging sessions
    """
    txn_id: str
    prev_hash: str
    timestamp: str
    amount: float
    status: str
    uid: str
    fid: str
    dispute_or_refund_flag: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "txn_id": self.txn_id,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "amount": self.amount,
            "status": self.status,
            "uid": self.uid,
            "fid": self.fid,
            "dispute_or_refund_flag": self.dispute_or_refund_flag,
        }
