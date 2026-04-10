from grid.grid import GridServer
from kiosk.kiosk import Kiosk
from user.user import UserClient


def main() -> None:
    """Entry point for the EV charging payment simulation."""
    grid = GridServer()
    kiosk = Kiosk(kiosk_id="KIOSK-001", grid=grid)
    user = UserClient(vmid="VMID-PLACEHOLDER")

    print("Project scaffold ready.")
    print(f"Grid: {grid}")
    print(f"Kiosk: {kiosk.kiosk_id}")
    print(f"User VMID: {user.vmid}")


if __name__ == "__main__":
    main()
