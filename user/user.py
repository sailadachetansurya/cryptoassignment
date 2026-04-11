from dataclasses import dataclass

from kiosk.kiosk import Kiosk


@dataclass
class UserClient:
    """Basic user client interface for building and submitting payments."""

    vmid: str

    def create_payment_request(self, pin: str, amount: float, qr_payload: str) -> dict[str, object]:
        """Build a payment request payload."""
        return {
            "vmid": self.vmid,
            "pin": pin,
            "amount": amount,
            "qr_payload": qr_payload,
        }

    def submit_payment(self, kiosk: Kiosk, pin: str, amount: float, qr_payload: str) -> dict[str, object]:
        """Submit a payment request to kiosk and return detailed status."""
        payload = self.create_payment_request(pin=pin, amount=amount, qr_payload=qr_payload)
        return kiosk.process_user_payment_detailed(
            vmid=str(payload["vmid"]),
            pin=str(payload["pin"]),
            amount=float(payload["amount"]),
            qr_payload=str(payload["qr_payload"]),
        )
