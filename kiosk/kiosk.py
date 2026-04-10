from dataclasses import dataclass

from grid.grid import GridServer


@dataclass
class Kiosk:
    """Placeholder kiosk that relays transactions to the grid."""

    kiosk_id: str
    grid: GridServer
    fid: str = "FID-PLACEHOLDER"

    def generate_qr_payload(self) -> str:
        """TODO: encrypt FID (or VFID) using ASCON and return QR payload string."""
        return "ENCRYPTED-FID-PLACEHOLDER"

    def verify_qr_payload(self, qr_payload: str) -> bool:
        """TODO: decrypt QR payload and validate station identity."""
        _ = qr_payload
        return True

    def forward_transaction(self, vmid: str, pin: str, amount: float, qr_payload: str) -> bool:
        """Forward request to grid after local QR verification."""
        if not self.verify_qr_payload(qr_payload):
            return False
        return self.grid.process_transaction(vmid=vmid, pin=pin, amount=amount, fid=self.fid)
