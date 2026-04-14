from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from crypto.ascon import decrypt_ascon, encrypt_ascon
from crypto.sha3 import sha3_bytes
from grid.grid import GridServer


@dataclass
class Kiosk:
    """Kiosk service that requests VFID generation and handles payment relay."""

    kiosk_id: str
    grid: GridServer
    fid: str = "FID-PLACEHOLDER"
    qr_payload: str = ""
    simulate_machine_failure: bool = False
    vfid_valid_window_seconds: int = 120
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

    def _validate_vfid_locally(self, qr_payload: str) -> tuple[bool, str]:
        """Decrypt and validate VFID ownership and freshness at kiosk before forwarding."""
        plaintext = decrypt_ascon(qr_payload, self.grid_master_key)
        if not plaintext or "|" not in plaintext:
            return False, "Invalid VFID QR String (Kiosk decryption failed)"

        vfid_fid, vfid_ts_raw = plaintext.split("|", 1)
        if vfid_fid != self.fid:
            return False, "QR does not belong to this kiosk franchise"

        try:
            vfid_ts = datetime.fromisoformat(vfid_ts_raw)
            if vfid_ts.tzinfo is None:
                vfid_ts = vfid_ts.replace(tzinfo=timezone.utc)
        except ValueError:
            return False, "Invalid VFID timestamp"

        age_seconds = (datetime.now(timezone.utc) - vfid_ts).total_seconds()
        if age_seconds < 0 or age_seconds > self.vfid_valid_window_seconds:
            return False, "VFID expired. Please refresh kiosk QR."
        return True, "VFID validated"

    def process_user_payment_encrypted(self, encrypted_payload: list[int], qr_payload: str) -> bool:
        """Validate VFID at kiosk and forward encrypted payment payload to the grid."""
        is_valid, message = self._validate_vfid_locally(qr_payload)
        if not is_valid:
            self.grid.last_result = {"ok": False, "message": message, "code": "KIOSK_VFID_REJECTED"}
            return False
        return self.grid.process_encrypted_transaction(encrypted_payload=encrypted_payload, vfid_str=qr_payload)

    def notify_franchise_of_approval(self) -> str:
        """Simulate sending the 'APPROVED' message to the Franchise system, which then unlocks the physical charger."""
        return f"Franchise {self.fid} received 'APPROVED'. Charger unlocked."

    def process_user_payment_detailed(
        self,
        vmid: str,
        pin: str,
        amount: float,
        qr_payload: str,
        encrypted_payload: list[int] | None = None,
    ) -> dict[str, Any]:
        """Process payment and return detailed status payload."""
        if encrypted_payload is not None:
            approved = self.process_user_payment_encrypted(encrypted_payload=encrypted_payload, qr_payload=qr_payload)
        else:
            approved = self.process_user_payment(vmid=vmid, pin=pin, amount=amount, qr_payload=qr_payload)
        result = self.grid.get_last_result()

        if approved and self.simulate_machine_failure:
            txn_id = result.get("txn_id")
            if txn_id:
                # Automatically reverse the transaction to simulate the machine dispense failing
                self.grid.refund_transaction(txn_id=txn_id, reason="Simulated Machine Failure")
                # But to the user app, we want to return a failure so they know
                result["approved"] = False
                result["status"] = "DISPENSE_FAILED"
                result["message"] = "Payment authorized, but kiosk hardware failed to dispense. Wallet refunded."
                return result

        if approved:
            # Kiosk signals the franchise, franchise replies with the unlock confirmation
            result["message"] = self.notify_franchise_of_approval()

        result["approved"] = approved
        result["status"] = self.display_status(approved)
        return result


    # -------------------------------------------------------------------------
    # Display Function
    # -------------------------------------------------------------------------

    def display_status(self, approved: bool) -> str:
        """Return a simple kiosk status message for the transaction result."""
        return "APPROVED" if approved else "REJECTED"
