from dataclasses import dataclass


@dataclass
class Block:
    """Placeholder blockchain block model."""

    txn_id: str
    prev_hash: str
    timestamp: str
    amount: float
    dispute_or_refund_flag: bool = False
