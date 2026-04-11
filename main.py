from grid.bootstrap import seed_required_grid_data
from grid.grid import GridServer
from kiosk.kiosk import Kiosk
from user.user import UserClient


def main() -> None:
    """Entry point for the EV charging payment simulation."""
    grid = GridServer()
    seed = seed_required_grid_data(grid)

    franchise = seed["franchises"][0]
    demo_user = seed["users"][0]

    kiosk = Kiosk(kiosk_id="KIOSK-001", grid=grid, fid=franchise["fid"])
    user = UserClient(vmid=demo_user["vmid"])

    qr_payload = kiosk.generate_qr_payload()
    result = user.submit_payment(kiosk=kiosk, pin=demo_user["pin"], amount=25.0, qr_payload=qr_payload)

    print("EV Charging Simulation")
    print(f"Provider count: {len(grid.provider_zones)}")
    print(f"Franchise FID: {franchise['fid']}")
    print(f"User VMID: {user.vmid}")
    print(f"Transaction status: {result['status']} | {result['message']}")

    if result.get("txn_id"):
        refunded = grid.refund_transaction(result["txn_id"], reason="Hardware failure")
        refund_result = grid.get_last_result()
        print(f"Refund issued: {refunded} | {refund_result['message']}")


if __name__ == "__main__":
    main()
