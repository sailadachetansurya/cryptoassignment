from __future__ import annotations

from flask import Flask, jsonify, request

from franchise.franchise import FranchiseClient
from grid.bootstrap import seed_required_grid_data
from grid.grid import GridServer
from kiosk.kiosk import Kiosk


app = Flask(__name__, static_folder="frontend", static_url_path="")

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
    mobile = str(data.get("mobile", ""))
    pin = str(data.get("pin", ""))
    initial_balance = float(data.get("initial_balance", 0.0))

    if not mobile or not pin:
        return jsonify({"ok": False, "message": "mobile and pin are required"}), 400

    uid, vmid = grid.register_user(mobile=mobile, pin=pin, initial_balance=initial_balance)
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
    return jsonify({"ok": True, "message": "User account closed"})


@app.post("/api/franchise/register")
def franchise_register() -> object:
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", ""))
    zone_code = str(data.get("zone_code", ""))
    password = str(data.get("password", ""))
    provider = str(data.get("provider", ""))
    initial_balance = float(data.get("initial_balance", 0.0))

    if not name or not zone_code or not password or not provider:
        return jsonify({"ok": False, "message": "name, provider, zone_code, and password are required"}), 400

    try:
        fid = franchise_client.register_franchise(
            name=name,
            zone_code=zone_code,
            password=password,
            initial_balance=initial_balance,
            provider=provider,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

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
    result = grid.get_last_result()
    status = 200 if ok else 400
    return jsonify(result), status


@app.post("/api/user/authorize")
def user_authorize() -> object:
    data = request.get_json(silent=True) or {}
    qr_payload = data.get("vfid_string") or data.get("qr_payload") or ""
    vmid_input = str(data.get("vmid", ""))
    pin_input = str(data.get("pin", ""))
    amount_input = data.get("amount", 0)

    try:
        amount = float(amount_input)
    except (TypeError, ValueError):
        return jsonify({"approved": False, "message": "Invalid amount."}), 400

    result = kiosk.process_user_payment_detailed(vmid=vmid_input, pin=pin_input, amount=amount, qr_payload=qr_payload)
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


if __name__ == "__main__":
    app.run(debug=True)
