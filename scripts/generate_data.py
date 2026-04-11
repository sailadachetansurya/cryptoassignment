import csv
import os
import random
from datetime import datetime, timezone

# Add the parent directory to the path so we can import from the project
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.sha3 import derive_fid, derive_uid, derive_vmid, sha3_hex

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FRANCHISES_CSV = os.path.join(DATA_DIR, "franchises.csv")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
TEST_CREDENTIALS_TXT = os.path.join(DATA_DIR, "test_credentials.txt")

FRANCHISE_NAMES = [
    "VoltCharge Central", "EcoJuice North", "NexGrid Plaza", "QuantumCharge Station",
    "SparkPoint Hub", "AeroCharge City", "ElectraDrive East", "ThunderGrid West",
    "PulsePower South", "NovaCharge Valley"
]

PROVIDERS = ["Tata Power", "Adani", "ChargePoint", "Reliance", "NTPC"]

USER_NAMES = [
    "Alice Smith", "Bob Johnson", "Charlie Davis", "Diana Evans", 
    "Ethan Foster", "Fiona Green", "George Harris", "Hannah Martin", 
    "Ian Clark", "Julia Lewis"
]

def generate_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    created_at_dt = datetime.now(timezone.utc).isoformat()

    franchise_credentials = []
    user_credentials = []

    print(f"Generating 10 realistic Franchises into {FRANCHISES_CSV}...")
    with open(FRANCHISES_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fid", "name", "provider", "zone", "password_hash", "balance"])
        
        for i, name in enumerate(FRANCHISE_NAMES):
            provider = random.choice(PROVIDERS)
            zone = f"ZONE-{i+1:02d}"
            password = f"secret{random.randint(100, 999)}"
            
            fid = derive_fid(name, zone, password, created_at_dt)
            pw_hash = sha3_hex(f"franchise:{password}")
            balance = round(random.uniform(500.0, 5000.0), 2)
            
            writer.writerow([fid, name, provider, zone, pw_hash, str(balance)])
            franchise_credentials.append((name, fid, password))

    print(f"Generating 10 realistic EV Owners into {USERS_CSV}...")
    with open(USERS_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["uid", "vmid", "name", "mobile", "pin_hash", "balance"])
        
        for name in USER_NAMES:
            mobile = f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"
            pin = f"{random.randint(1000, 9999)}"
            
            uid = derive_uid(mobile, pin)
            vmid = derive_vmid(uid, mobile)
            pin_hash = sha3_hex(f"pin:{pin}")
            balance = round(random.uniform(50.0, 500.0), 2)
            
            writer.writerow([uid, vmid, name, mobile, pin_hash, str(balance)])
            user_credentials.append((name, mobile, vmid, pin))

    print(f"Writing cleartext testing credentials to {TEST_CREDENTIALS_TXT}...")
    with open(TEST_CREDENTIALS_TXT, mode="w", encoding="utf-8") as f:
        f.write("=== EV CHARGING PAYMENT GATEWAY: TEST CREDENTIALS ===\n")
        f.write("Do not use these in production. This is for grading/testing purposes.\n\n")
        
        f.write("--- EV OWNERS (Use these to test the Frontend UI) ---\n")
        for u_name, mobile, vmid, pin in user_credentials:
            f.write(f"Name: {u_name.ljust(15)} | Mobile: {mobile} | VMID: {vmid} | PIN: {pin}\n")
            
        f.write("\n--- FRANCHISES (For backend/kiosk testing) ---\n")
        for f_name, fid, password in franchise_credentials:
            f.write(f"Name: {f_name.ljust(20)} | FID: {fid} | Password: {password}\n")

    print("\nData generation complete! You can run the app now.")

if __name__ == "__main__":
    generate_data()
