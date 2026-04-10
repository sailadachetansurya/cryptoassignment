from dataclasses import dataclass, field
from typing import Any


@dataclass
class GridServer:
    """Placeholder grid authority service."""

    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    franchises: dict[str, dict[str, Any]] = field(default_factory=dict)
    blockchain: list[dict[str, Any]] = field(default_factory=list)

    def register_user(self, mobile: str, pin: str) -> str:
        """TODO: implement UID and VMID generation logic."""
        uid = "UID-PLACEHOLDER"
        self.users[uid] = {"mobile": mobile, "pin": pin, "balance": 0}
        return uid

    def register_franchise(self, name: str, zone_code: str, password: str) -> str:
        """TODO: implement FID generation logic."""
        fid = "FID-PLACEHOLDER"
        self.franchises[fid] = {"name": name, "zone": zone_code, "password": password}
        return fid

    def process_transaction(self, vmid: str, pin: str, amount: float, fid: str) -> bool:
        """TODO: validate VMID/PIN/balance, transfer funds, and append blockchain block."""
        _ = (vmid, pin, amount, fid)
        return False
