from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from crypto.ascon import encrypt_ascon, decrypt_ascon
from crypto.sha3 import derive_fid, derive_transaction_id, derive_uid, derive_vmid, sha3_hex, verify_sha3, sha3_bytes


@dataclass
class GridServer:
    """Grid authority service for registration, validation, and ledger writes."""

    provider_zones: dict[str, list[str]] = field(default_factory=dict)
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    users_by_vmid: dict[str, str] = field(default_factory=dict)
    franchises: dict[str, dict[str, Any]] = field(default_factory=dict)
    blockchain: list[dict[str, Any]] = field(default_factory=list)
    last_result: dict[str, Any] = field(default_factory=lambda: {"ok": True, "message": "Ready"})
    grid_master_key: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Derive a stable grid master key for ASCON encryption."""
        self.grid_master_key = sha3_bytes("GRID_MASTER_SECRET_2026")[:16]

    def decrypt_vfid(self, vfid_str: str) -> tuple[str | None, str | None]:
        """Decrypt the LWC VFID string sent from the user app back into the original Kiosk FID and timestamp."""
        plaintext = decrypt_ascon(vfid_str, self.grid_master_key)
        if not plaintext or '|' not in plaintext:
            return None, None
        fid, timestamp = plaintext.split('|', 1)
        return fid, timestamp

    def initialize_grid(self, provider_zones: dict[str, list[str]]) -> None:
        """Initialize provider-to-zone mappings for franchise validation."""
        self.provider_zones = {provider: list(zones) for provider, zones in provider_zones.items()}

    def _is_valid_zone(self, zone_code: str, provider: str | None = None) -> bool:
        """Validate zone against configured providers."""
        if not self.provider_zones:
            return True
        if provider:
            return zone_code in self.provider_zones.get(provider, [])
        return any(zone_code in zones for zones in self.provider_zones.values())

    @staticmethod
    def _hash_pin(pin: str) -> str:
        """Hash PIN before storing."""
        return sha3_hex(f"pin:{pin}")

    def get_last_result(self) -> dict[str, Any]:
        """Return the most recent transaction result payload."""
        return dict(self.last_result)

    def register_user(self, mobile: str, pin: str, initial_balance: float = 0.0) -> tuple[str, str]:
        """Register a user and return (uid, vmid)."""
        uid = derive_uid(mobile, pin)
        vmid = derive_vmid(uid, mobile)
        self.users[uid] = {
            "mobile": mobile,
            "pin_hash": self._hash_pin(pin),
            "balance": float(initial_balance),
            "vmid": vmid,
            "active": True,
        }
        self.users_by_vmid[vmid] = uid
        return uid, vmid

    def close_user_account(self, vmid: str) -> bool:
        """Deactivate a user account to simulate account closure edge case."""
        uid = self.users_by_vmid.get(vmid)
        if not uid:
            return False
        self.users[uid]["active"] = False
        return True

    def register_franchise(
        self,
        name: str,
        zone_code: str,
        password: str,
        initial_balance: float = 0.0,
        provider: str | None = None,
    ) -> str:
        """Register a franchise and return fid."""
        if not self._is_valid_zone(zone_code=zone_code, provider=provider):
            raise ValueError("Invalid zone code for configured provider mapping")

        created_at = datetime.now(timezone.utc).isoformat()
        fid = derive_fid(name, zone_code, password, created_at)
        self.franchises[fid] = {
            "name": name,
            "provider": provider,
            "zone": zone_code,
            "password_hash": sha3_hex(f"franchise:{password}"),
            "balance": float(initial_balance),
        }
        return fid

    def _append_block(
        self,
        txn_id: str,
        amount: float,
        status: str,
        uid: str,
        fid: str,
        dispute_or_refund_flag: bool = False,
    ) -> None:
        """Append a transaction block to the centralized blockchain list."""
        prev_hash = self.blockchain[-1]["txn_id"] if self.blockchain else "GENESIS"
        self.blockchain.append(
            {
                "txn_id": txn_id,
                "prev_hash": prev_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "amount": float(amount),
                "status": status,
                "uid": uid,
                "fid": fid,
                "dispute_or_refund_flag": dispute_or_refund_flag,
            }
        )

    def get_ledger(self) -> list[dict[str, Any]]:
        """Return a copy of the current ledger."""
        return list(self.blockchain)

    def process_transaction(self, vmid: str, pin: str, amount: float, vfid_str: str) -> bool:
        """Validate VFID, VMID/PIN/funds, transfer funds, and append a block."""
        fid, timestamp = self.decrypt_vfid(vfid_str)
        if not fid:
            self.last_result = {"ok": False, "message": "Invalid VFID QR String (Decryption failed)", "code": "QR_MISMATCH"}
            return False
            
        uid = self.users_by_vmid.get(vmid)
        if not uid:
            self.last_result = {"ok": False, "message": "VMID not found", "code": "VMID_NOT_FOUND"}
            return False
        if fid not in self.franchises:
            self.last_result = {"ok": False, "message": "Invalid franchise decoded", "code": "FID_NOT_FOUND"}
            return False

        user = self.users[uid]
        franchise = self.franchises[fid]

        if not user["active"]:
            self.last_result = {"ok": False, "message": "User account is closed", "code": "ACCOUNT_CLOSED"}
            return False

        if not verify_sha3(f"pin:{pin}", user["pin_hash"]):
            self.last_result = {"ok": False, "message": "Invalid PIN", "code": "INVALID_PIN"}
            return False
        if amount <= 0:
            self.last_result = {"ok": False, "message": "Amount must be positive", "code": "INVALID_AMOUNT"}
            return False
        if user["balance"] < amount:
            self.last_result = {"ok": False, "message": "Insufficient balance", "code": "INSUFFICIENT_BALANCE"}
            return False

        user["balance"] -= amount
        franchise["balance"] += amount

        ts = datetime.now(timezone.utc).isoformat()
        txn_id = derive_transaction_id(uid=uid, fid=fid, timestamp=ts, amount=f"{amount:.2f}")
        self._append_block(txn_id=txn_id, amount=amount, status="Success", uid=uid, fid=fid)
        self.last_result = {
            "ok": True,
            "message": "Payment Authorized. Charging Started!",
            "code": "APPROVED",
            "txn_id": txn_id,
        }
        return True

    def refund_transaction(self, txn_id: str, reason: str = "Hardware failure") -> bool:
        """Append a reversal block and transfer funds back from franchise to user."""
        for block in self.blockchain:
            if block["txn_id"] != txn_id:
                continue
            if block["dispute_or_refund_flag"]:
                self.last_result = {"ok": False, "message": "Transaction already refunded", "code": "ALREADY_REFUNDED"}
                return False

            uid = block["uid"]
            fid = block["fid"]
            amount = float(block["amount"])
            if uid not in self.users or fid not in self.franchises:
                self.last_result = {"ok": False, "message": "Refund parties missing", "code": "REFUND_PARTIES_MISSING"}
                return False

            if self.franchises[fid]["balance"] < amount:
                self.last_result = {
                    "ok": False,
                    "message": "Franchise balance insufficient for refund",
                    "code": "REFUND_INSUFFICIENT_FRANCHISE_BALANCE",
                }
                return False

            self.franchises[fid]["balance"] -= amount
            self.users[uid]["balance"] += amount
            block["dispute_or_refund_flag"] = True

            refund_txn_id = derive_transaction_id(
                uid=uid,
                fid=fid,
                timestamp=datetime.now(timezone.utc).isoformat(),
                amount=f"-{amount:.2f}",
            )
            self._append_block(
                txn_id=refund_txn_id,
                amount=-amount,
                status=f"Refunded: {reason}",
                uid=uid,
                fid=fid,
                dispute_or_refund_flag=True,
            )
            self.last_result = {
                "ok": True,
                "message": "Refund completed",
                "code": "REFUND_COMPLETED",
                "txn_id": refund_txn_id,
            }
            return True

        self.last_result = {"ok": False, "message": "Transaction not found", "code": "TXN_NOT_FOUND"}
        return False
