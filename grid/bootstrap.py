from __future__ import annotations

from grid.grid import GridServer


REQUIRED_PROVIDER_ZONES = {
    "Tata Power": ["TP-Z1", "TP-Z2", "TP-Z3"],
    "Adani": ["AD-Z1", "AD-Z2", "AD-Z3"],
    "ChargePoint": ["CP-Z1", "CP-Z2", "CP-Z3"],
}


def seed_required_grid_data(grid: GridServer) -> dict[str, object]:
    """Seed provider/zone mappings, baseline franchises, and demo users."""
    grid.initialize_grid(REQUIRED_PROVIDER_ZONES)

    franchises: list[dict[str, str]] = []
    for provider, zones in REQUIRED_PROVIDER_ZONES.items():
        for zone in zones:
            name = f"{provider} {zone} Station"
            password = f"{zone.lower()}-pass"
            fid = grid.register_franchise(
                name=name,
                zone_code=zone,
                password=password,
                initial_balance=1000.0,
                provider=provider,
            )
            franchises.append({"provider": provider, "zone": zone, "name": name, "fid": fid})

    users: list[dict[str, str]] = []
    user_rows = [
        ("9999999999", "1234", 500.0),
        ("8888888888", "5678", 350.0),
        ("7777777777", "2468", 800.0),
    ]
    for mobile, pin, balance in user_rows:
        uid, vmid = grid.register_user(mobile=mobile, pin=pin, initial_balance=balance)
        users.append({"mobile": mobile, "pin": pin, "uid": uid, "vmid": vmid})

    return {
        "providers": REQUIRED_PROVIDER_ZONES,
        "franchises": franchises,
        "users": users,
    }
