from __future__ import annotations

from dataclasses import dataclass

from grid.grid import GridServer
from kiosk.kiosk import Kiosk


@dataclass
class FranchiseClient:
    """Franchise-facing helper functions for kiosk and grid interactions."""

    grid: GridServer
    kiosk: Kiosk

    def register_franchise(
        self,
        name: str,
        zone_code: str,
        password: str,
        initial_balance: float,
        provider: str,
    ) -> str:
        """Register a franchise and bind kiosk identity to returned FID."""
        fid = self.grid.register_franchise(
            name=name,
            zone_code=zone_code,
            password=password,
            initial_balance=initial_balance,
            provider=provider,
        )
        self.kiosk.set_franchise_identity(fid)
        return fid

    def generate_station_qr_payload(self) -> str:
        """Generate a fresh encrypted payload for kiosk display."""
        return self.kiosk.generate_qr_payload()

    def get_franchise_balance(self, fid: str) -> float:
        """Read the current franchise balance from grid memory."""
        return float(self.grid.franchises[fid]["balance"])
