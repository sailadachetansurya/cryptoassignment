from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from crypto.ascon import encrypt_ascon
from crypto.sha3 import sha3_bytes
from grid.grid import GridServer


@dataclass
class Kiosk:
    """Kiosk service that requests VFID generation and handles payment relay."""

    kiosk_id: str
    grid: GridServer
    fid: str = "FID-PLACEHOLDER"
    qr_payload: str = ""
    grid_master_key: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Kiosk uses the identical Grid pre-shared key for ASCON payloads in this demo."""
        self.grid_master_key = sha3_bytes("GRID_MASTER_SECRET_2026")[:16]

    # -------------------------------------------------------------------------
    # Franchise Endpoint Functions
    # -------------------------------------------------------------------------

    def set_franchise_identity(self, fid: str) -> None:
        """Set the active franchise identity for this kiosk."""
        self.fid = fid

    def generate_qr_payload(self) -> str:
        """The Kiosk (LWC) encrypts its stored FID and current timestamp using ASCON."""
        timestamp = datetime.now(timezone.utc).isoformat()
        plaintext = f"{self.fid}|{timestamp}"
        self.qr_payload = encrypt_ascon(plaintext, self.grid_master_key)
        return self.qr_payload

    def get_franchise_qr_payload(self) -> str:
        """Return the current QR payload for display on the kiosk screen."""
        if not self.qr_payload:
            return self.generate_qr_payload()
        return self.qr_payload


    # -------------------------------------------------------------------------
    # User Endpoint Functions
    # -------------------------------------------------------------------------

    def build_user_payment_request(self, vmid: str, pin: str, amount: float, qr_payload: str) -> dict[str, object]:
        """Build the kiosk-side request object from user supplied data."""
        return {
            "vmid": vmid,
            "pin": pin,
            "amount": amount,
            "qr_payload": qr_payload,
        }


    def process_user_payment(self, vmid: str, pin: str, amount: float, qr_payload: str) -> bool:
        """Pass the payment request directly to the grid server so it handles decryption and verification."""
        return self.grid.process_transaction(vmid=vmid, pin=pin, amount=amount, vfid_str=qr_payload)

    def process_user_payment_detailed(self, vmid: str, pin: str, amount: float, qr_payload: str) -> dict[str, Any]:
        """Process payment and return detailed status payload."""
        approved = self.process_user_payment(vmid=vmid, pin=pin, amount=amount, qr_payload=qr_payload)
        result = self.grid.get_last_result()
        result["approved"] = approved
        result["status"] = self.display_status(approved)
        return result


    # -------------------------------------------------------------------------
    # Display Function
    # -------------------------------------------------------------------------

    def display_status(self, approved: bool) -> str:
        """Return a simple kiosk status message for the transaction result."""
        return "APPROVED" if approved else "REJECTED"
