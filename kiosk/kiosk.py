from dataclasses import dataclass, field
from typing import Any

from crypto.ascon import decrypt_ascon, encrypt_ascon
from crypto.sha3 import sha3_bytes
from grid.grid import GridServer


@dataclass
class Kiosk:
    """Kiosk service that handles QR generation, verification, and payment relay."""

    kiosk_id: str
    grid: GridServer
    fid: str = "FID-PLACEHOLDER"
    qr_payload: str = ""
    crypto_key: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Derive a stable per-kiosk key used for ASCON QR payloads."""
        self.crypto_key = sha3_bytes(f"kiosk:{self.kiosk_id}")[:16]


    # -------------------------------------------------------------------------
    # Franchise Endpoint Functions
    # -------------------------------------------------------------------------

    def set_franchise_identity(self, fid: str) -> None:
        """Set the active franchise identity for this kiosk."""
        self.fid = fid

    def generate_qr_payload(self) -> str:
        """Encrypt the kiosk's FID and return a QR-ready payload string."""
        self.qr_payload = encrypt_ascon(self.fid, self.crypto_key)
        return self.qr_payload

    def get_franchise_qr_payload(self) -> str:
        """Return the current QR payload for display on the kiosk screen."""
        if not self.qr_payload:
            return self.generate_qr_payload()
        return self.qr_payload


    # -------------------------------------------------------------------------
    # User Endpoint Functions
    # -------------------------------------------------------------------------

    def verify_qr_payload(self, qr_payload: str) -> bool:
        """Decrypt a QR payload and confirm it matches the kiosk FID."""
        recovered_fid = decrypt_ascon(qr_payload, self.crypto_key)
        return bool(recovered_fid) and recovered_fid == self.fid

    def build_user_payment_request(self, vmid: str, pin: str, amount: float, qr_payload: str) -> dict[str, object]:
        """Build the kiosk-side request object from user supplied data."""
        return {
            "vmid": vmid,
            "pin": pin,
            "amount": amount,
            "qr_payload": qr_payload,
        }


    def process_user_payment(self, vmid: str, pin: str, amount: float, qr_payload: str) -> bool:
        """Validate the user QR payload and send the payment to the grid."""
        if not self.verify_qr_payload(qr_payload):
            self.grid.last_result = {"ok": False, "message": "QR/FID mismatch", "code": "QR_MISMATCH"}
            return False
        return self.forward_transaction(vmid=vmid, pin=pin, amount=amount)

    def process_user_payment_detailed(self, vmid: str, pin: str, amount: float, qr_payload: str) -> dict[str, Any]:
        """Process payment and return detailed status payload."""
        approved = self.process_user_payment(vmid=vmid, pin=pin, amount=amount, qr_payload=qr_payload)
        result = self.grid.get_last_result()
        result["approved"] = approved
        result["status"] = self.display_status(approved)
        return result


    # -------------------------------------------------------------------------
    # Grid Endpoint Functions
    # -------------------------------------------------------------------------

    def forward_transaction(self, vmid: str, pin: str, amount: float) -> bool:
        """Forward a validated payment request to the grid server."""
        return self.grid.process_transaction(vmid=vmid, pin=pin, amount=amount, fid=self.fid)

    def display_status(self, approved: bool) -> str:
        """Return a simple kiosk status message for the transaction result."""
        return "APPROVED" if approved else "REJECTED"
