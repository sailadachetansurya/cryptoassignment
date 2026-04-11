from __future__ import annotations
import csv
import os
import subprocess
from datetime import datetime, timezone

from crypto.sha3 import derive_fid, derive_uid, derive_vmid, sha3_hex
from grid.grid import GridServer

REQUIRED_PROVIDER_ZONES = {
    "Tata Power": ["TP-Z1", "TP-Z2", "TP-Z3"],
    "Adani": ["AD-Z1", "AD-Z2", "AD-Z3"],
    "ChargePoint": ["CP-Z1", "CP-Z2", "CP-Z3"],
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FRANCHISES_CSV = os.path.join(DATA_DIR, "franchises.csv")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")

def _init_csv_files() -> None:
    """Generate default CSV data using the generate file if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(FRANCHISES_CSV) or not os.path.exists(USERS_CSV):
        gen_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "generate_data.py")
        subprocess.run(["python", gen_script], check=True)

def seed_required_grid_data(grid: GridServer) -> dict[str, object]:
    """Seed provider/zone mappings, then load existing franchises and users from CSVs."""
    grid.initialize_grid(REQUIRED_PROVIDER_ZONES)
    _init_csv_files()

    franchises_list = []
    with open(FRANCHISES_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fid = row["fid"]
            grid.franchises[fid] = {
                "name": row["name"],
                "provider": row["provider"],
                "zone": row["zone"],
                "password_hash": row["password_hash"], # Never plaintext in CSV
                "balance": float(row["balance"]),
            }
            franchises_list.append({"fid": fid, "name": row["name"], "provider": row["provider"], "zone": row["zone"]})

    users_list = []
    with open(USERS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = row["uid"]
            vmid = row["vmid"]
            mobile = row["mobile"]
            grid.users[uid] = {
                "mobile": mobile,
                "pin_hash": row["pin_hash"], # Never plaintext in CSV
                "balance": float(row["balance"]),
                "vmid": vmid,
                "active": True,
            }
            grid.users_by_vmid[vmid] = uid
            # The PIN is not sent here since it shouldn't be read from the DB into memory
            # Use `data/test_credentials.txt` to find testing PINs
            users_list.append({"uid": uid, "vmid": vmid, "mobile": mobile})

    return {
        "providers": REQUIRED_PROVIDER_ZONES,
        "franchises": franchises_list,
        "users": users_list,
    }
