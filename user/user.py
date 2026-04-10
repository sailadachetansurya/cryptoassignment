from dataclasses import dataclass


@dataclass
class UserClient:
    """Placeholder user client interface."""

    vmid: str

    def create_payment_request(self, pin: str, amount: float, qr_payload: str) -> dict[str, object]:
        """TODO: hash/encrypt sensitive fields before sending."""
        return {
            "vmid": self.vmid,
            "pin": pin,
            "amount": amount,
            "qr_payload": qr_payload,
        }
