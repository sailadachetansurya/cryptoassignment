from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

from franchise.franchise import FranchiseClient
from grid.bootstrap import seed_required_grid_data, sync_users_to_csv, sync_franchises_to_csv, append_to_test_credentials
from grid.grid import GridServer
from kiosk.kiosk import Kiosk


app = Flask(__name__, static_folder="frontend", static_url_path="")

SNOOP_LOG_PATH = (Path(__file__).resolve().parent / "snoop_packet.log")


def log_snoop_packet(packet_type: str, encrypted_payload: list[int], meta: dict[str, object] | None = None) -> None:
    """Append intercepted RSA payload metadata for demo wiretap simulation."""
    try:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "packet_type": packet_type,
            "n": 3233,
            "e": 17,
            "encrypted_payload": encrypted_payload,
            "meta": meta or {},
        }
        with SNOOP_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Snoop logging must never break the main transaction flow.
        pass


def _read_snoop_entries(limit: int = 20) -> list[dict[str, object]]:
    """Read the latest snoop log entries (most recent first)."""
    if not SNOOP_LOG_PATH.exists() or SNOOP_LOG_PATH.stat().st_size == 0:
        return []

    with SNOOP_LOG_PATH.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    entries: list[dict[str, object]] = []
    for line in reversed(lines[-max(1, limit):]):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


grid = GridServer()
seed_data = seed_required_grid_data(grid)
first_franchise = seed_data["franchises"][0]
demo_user_record = seed_data["users"][0]

kiosk = Kiosk(kiosk_id="KIOSK-001", grid=grid, fid=first_franchise["fid"])
franchise_client = FranchiseClient(grid=grid, kiosk=kiosk)


@app.get("/")
def index() -> object:
    return app.send_static_file("index.html")


@app.get("/api/kiosk/generate_vfid")
def generate_vfid() -> object:
    payload = kiosk.generate_qr_payload()
    return jsonify({"vfid": payload, "fid": kiosk.fid})


@app.get("/api/grid/config")
def grid_config() -> object:
    return jsonify({"provider_zones": grid.provider_zones})


@app.post("/api/user/register")
def user_register() -> object:
    data = request.get_json(silent=True) or {}
    encrypted_payload = data.get("encrypted_payload")

    if not isinstance(encrypted_payload, list) or not encrypted_payload:
        return jsonify({"ok": False, "message": "encrypted_payload is required"}), 400

    try:
        uid, vmid, name, mobile, pin = grid.register_user_encrypted(encrypted_payload)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    log_snoop_packet(
        packet_type="user_registration",
        encrypted_payload=encrypted_payload,
        meta={"uid": uid, "vmid": vmid, "mobile": mobile},
    )

    sync_users_to_csv(grid)
    append_to_test_credentials("EV OWNER", f"Name: {name.ljust(15)} | Mobile: {mobile} | VMID: {vmid} | PIN: {pin}")

    return jsonify({"ok": True, "uid": uid, "vmid": vmid})


@app.get("/api/user/list")
def user_list() -> object:
    rows = []
    for uid, user in grid.users.items():
        rows.append(
            {
                "uid": uid,
                "vmid": user["vmid"],
                "mobile": user["mobile"],
                "balance": user["balance"],
                "active": user["active"],
            }
        )
    return jsonify(rows)


@app.post("/api/user/close")
def user_close() -> object:
    data = request.get_json(silent=True) or {}
    vmid_input = str(data.get("vmid", ""))
    ok = grid.close_user_account(vmid_input)
    if not ok:
        return jsonify({"ok": False, "message": "VMID not found"}), 404
    sync_users_to_csv(grid)
    return jsonify({"ok": True, "message": "User account deactivated"})

@app.post("/api/user/activate")
def user_activate() -> object:
    data = request.get_json(silent=True) or {}
    vmid_input = str(data.get("vmid", ""))
    ok = grid.activate_user_account(vmid_input)
    if not ok:
        return jsonify({"ok": False, "message": "VMID not found"}), 404
    sync_users_to_csv(grid)
    return jsonify({"ok": True, "message": "User account activated"})


@app.post("/api/franchise/register")
def franchise_register() -> object:
    data = request.get_json(silent=True) or {}
    encrypted_payload = data.get("encrypted_payload")

    if not isinstance(encrypted_payload, list) or not encrypted_payload:
        return jsonify({"ok": False, "message": "encrypted_payload is required"}), 400

    try:
        fid, name, password = grid.register_franchise_encrypted(encrypted_payload)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    log_snoop_packet(
        packet_type="franchise_registration",
        encrypted_payload=encrypted_payload,
        meta={"fid": fid, "name": name},
    )

    sync_franchises_to_csv(grid)
    append_to_test_credentials("FRANCHISE", f"Name: {name.ljust(20)} | FID: {fid} | Password: {password}")

    qr_payload = franchise_client.generate_station_qr_payload()
    return jsonify({"ok": True, "fid": fid, "qr_payload": qr_payload})


@app.get("/api/franchise/list")
def franchise_list() -> object:
    rows = []
    for fid, franchise in grid.franchises.items():
        rows.append(
            {
                "fid": fid,
                "name": franchise["name"],
                "provider": franchise.get("provider"),
                "zone": franchise["zone"],
                "balance": franchise["balance"],
            }
        )
    return jsonify(rows)


@app.post("/api/user/add_balance")
def user_add_balance() -> object:
    data = request.get_json(silent=True) or {}
    vmid = str(data.get("vmid", ""))
    amount = float(data.get("amount", 0.0))
    if not vmid or amount <= 0:
        return jsonify({"ok": False, "message": "vmid and positive amount required"}), 400
    uid = grid.users_by_vmid.get(vmid)
    if not uid:
        return jsonify({"ok": False, "message": "User not found"}), 404
    grid.users[uid]["balance"] += amount
    sync_users_to_csv(grid)
    return jsonify({"ok": True, "new_balance": grid.users[uid]["balance"]})

@app.post("/api/franchise/add_balance")
def franchise_add_balance() -> object:
    data = request.get_json(silent=True) or {}
    fid = str(data.get("fid", ""))
    amount = float(data.get("amount", 0.0))
    if not fid or amount <= 0:
        return jsonify({"ok": False, "message": "fid and positive amount required"}), 400
    if fid not in grid.franchises:
        return jsonify({"ok": False, "message": "Franchise not found"}), 404
    grid.franchises[fid]["balance"] += amount
    sync_franchises_to_csv(grid)
    return jsonify({"ok": True, "new_balance": grid.franchises[fid]["balance"]})

@app.post("/api/franchise/switch")
def franchise_switch() -> object:
    data = request.get_json(silent=True) or {}
    fid_input = str(data.get("fid", ""))
    if fid_input not in grid.franchises:
        return jsonify({"ok": False, "message": "FID not found"}), 404
    kiosk.set_franchise_identity(fid_input)
    payload = kiosk.generate_qr_payload()
    return jsonify({"ok": True, "fid": fid_input, "qr_payload": payload})


@app.post("/api/grid/refund")
def grid_refund() -> object:
    data = request.get_json(silent=True) or {}
    txn_id = str(data.get("txn_id", ""))
    reason = str(data.get("reason", "Hardware failure"))
    if not txn_id:
        return jsonify({"ok": False, "message": "txn_id is required"}), 400

    ok = grid.refund_transaction(txn_id=txn_id, reason=reason)
    if ok:
        sync_users_to_csv(grid)
        sync_franchises_to_csv(grid)

    result = grid.get_last_result()
    status = 200 if ok else 400
    return jsonify(result), status

@app.post("/api/kiosk/simulate_failure")
def simulate_kiosk_failure() -> object:
    data = request.get_json(silent=True) or {}
    fail_mode = bool(data.get("fail", False))
    kiosk.simulate_machine_failure = fail_mode
    return jsonify({"ok": True, "simulate_machine_failure": kiosk.simulate_machine_failure})


@app.post("/api/user/authorize")
def user_authorize() -> object:
    data = request.get_json(silent=True) or {}
    qr_payload = data.get("vfid_string") or data.get("qr_payload") or ""
    encrypted_payload = data.get("encrypted_payload")

    if not isinstance(encrypted_payload, list) or not encrypted_payload:
        return jsonify({"approved": False, "message": "encrypted_payload is required"}), 400

    log_snoop_packet(
        packet_type="user_payment_authorize",
        encrypted_payload=encrypted_payload,
        meta={"vfid": qr_payload},
    )

    result = kiosk.process_user_payment_detailed(
        vmid="",
        pin="",
        amount=0.0,
        qr_payload=qr_payload,
        encrypted_payload=encrypted_payload,
    )
    if result["approved"]:
        sync_users_to_csv(grid)
        sync_franchises_to_csv(grid)

    status_code = 200 if result["approved"] else 400
    return jsonify(result), status_code


@app.get("/api/grid/ledger")
def grid_ledger() -> object:
    blocks = grid.get_ledger()
    rows = []
    for block in reversed(blocks):
        rows.append(
            {
                "time": block["timestamp"],
                "hash": block["txn_id"],
                "amount": f"${block['amount']:.2f}",
                "status": block.get("status", "Success"),
                "dispute_or_refund_flag": block.get("dispute_or_refund_flag", False),
            }
        )
    return jsonify(rows)


@app.get("/api/demo/user")
def demo_user() -> object:
    return jsonify({"vmid": demo_user_record["vmid"], "mobile": demo_user_record["mobile"]})


@app.get("/api/attacker/packets")
def attacker_packets() -> object:
    """Expose intercepted packets with simulated Shor-attack preview for dashboard."""
    limit_raw = request.args.get("limit", "20")
    try:
        limit = int(limit_raw)
    except ValueError:
        limit = 20
    limit = max(1, min(limit, 100))

    entries = _read_snoop_entries(limit=limit)
    return jsonify({"entries": entries, "snoop_log_path": str(SNOOP_LOG_PATH)})


if __name__ == "__main__":
    app.run(debug=True)
