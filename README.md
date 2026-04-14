# BITSF463_Team_4 — Secure Centralized EV Charging Payment Gateway

**Cryptography Term Project 2025-26**

## 1. Project Overview
This project implements a simulation of a secure EV Charging Payment Gateway that combines Blockchain, Lightweight Cryptography (ASCON), and Quantum Cryptography concepts to build a tamper-resistant, efficient billing/payment system for EV charging franchises. It follows the professor's official problem statement, using well-specified registration, transaction flows, cryptographic primitives, and system entities (Kiosk, Grid Authority, Franchise, User/EV Owner).

## 2. Team Members
| Name                        | ID            |
| --------------------------- | ------------- |
| Yakali Vivek                | 2023A7PS0029H |
| Sasanka Allamaraju          | 2023A7PS0145H |
| Kalipatnapu Vivek           | 2023A7PS0169H |
| Chetan Surya                | 2023A7PS0023H |
| Adarsh Chakravarthy Vaddadi | 2023A7PS0089H |

## 3. Installation & Dependencies
- Python >= 3.12
- `ascon`, `flask`

### Using `uv` (recommended)
```
uv pip install -r requirements.txt
```
Or, to install dependencies directly:
```
uv pip install ascon flask
```

### Using pip (alternative)
```
pip install -r requirements.txt
```

## 4. How to Run / Demo
1. **Simulation (CLI entry):**
   ```
   python main.py
   ```
   This seeds grid/users/franchises, runs a typical transaction, and demonstrates refund/reversal flows.

2. **Web/API Mode:**
   ```
   python app.py
   ```
   Flask endpoints for registration, payment, balance check, etc.

3. **Quantum Cryptography Demo (Shor's RSA break/attacker):**
   ```
   python quantum/shor_demo.py --follow
   ```
   This simulates Shor's algorithm factoring a small RSA public-key exchange and shows plaintext extraction from intercepted registration/payment packets. 
   The tool cracks and displays the decrypted registration/payment PIN and user info, live, simulating quantum vulnerability.

   - For live attack on the most recent packet:
     ```
     python quantum/shor_demo.py --live-attack
     ```

   - All keys demonstrated are intentionally toy-sized and should never be used outside quantum-vulnerability demos.

## 5. Core Features & Technologies
- **ASCON LWC**: Franchise IDs and payment QR/VFID payloads are encrypted using ASCON (to simulate real LWC on constrained kiosks).
- **SHA-3/Keccak Hashing**: Used for UID, FID, VMID, and block IDs; all transaction/integrity hashes.
- **Blockchain Ledger**: Every valid transaction is stored in an immutable, tamper-evident chain. Each block includes: txn ID, previous hash, amount, timestamp, and dispute/refund flags (for chargebacks or hardware issues).
- **Quantum Crypto Simulation**: Our code includes a purely classical Shor's attack demo on toy RSA, per the spec; a dedicated snoop log is maintained solely for demonstrating the break. This log should NOT be used in real deployments!

## 6. Edge Cases & Design Assumptions
- *Account can be closed* mid-session; deactivated accounts are rejected for new transactions.
- For demo, QR code payload is a string (encrypted); displaying as image/QR can be added.

### 6.1 Provider/Zone Registration & User Account Assumptions
- **User registration is zone-independent:**
  - Users create accounts directly with the Grid by providing only `name`, `mobile`, `pin`, and `initial_balance`.
  - Users do **not** specify or require a `provider` or `zone_code`. User accounts are global within the system.
  - `mobile` and `pin` are mandatory; name is optional (default fallback permitted for demo). `initial_balance` must be a valid non-negative number.
- **Franchises must register with provider and zone:**
  - Franchise registration requires: `name`, `provider`, `zone_code`, `password`, `initial_balance`.
  - Zone validity is checked against a Grid-configured provider-zone mapping (`provider_zones`).
  - All required fields must be present and valid; otherwise, registration fails.

### 6.2 Cryptographic Payload & Security Assumptions
- **Universal Encryption Key:** All registration and payment data is encrypted by the frontend using a single Grid Authority public key before being sent to the backend. No sensitive user/franchise data (PINs, passwords, VMID, etc.) ever travels in the clear, ensuring confidentiality even in the presence of untrusted or compromised intermediaries (Kiosk, Franchise, etc.).
- **Backend-Only Decryption:** The private key for this RSA keypair is held only by the Grid Authority. Only the Grid can decrypt and access these fields. No per-user or per-franchise keys are issued because only the Grid needs to decrypt any secrets for account setup and payment (trusted central validation model).
- **Design Reasoning:** This design is intentional: Since Grid is the only validator/integrity-custodian in the network, one public/private keypair is sufficient, greatly simplifying deployment while ensuring all sensitive data is only visible to the Grid.
- All registration and payment data (user and franchise) is sent as RSA-encrypted integer arrays (`encrypted_payload`) for classical/quantum vulnerability demonstration purposes.
- Demo RSA key is intentionally tiny (`n=3233, e=17`) for Shor-vulnerability demonstration.
- Payment payload includes `{ pin, vmid, amount, vfid }` so session context is securely bound and replay is mitigated.
- Kiosk validates VFID freshness and franchise match before forwarding to Grid; Grid confirms VFID and applies PIN/funds/balance checks.

### 6.3 Demo & Attacker Logging Assumptions
- Intercepted packets are appended to `snoop_packet.log` (educational demo only).
- Cracked attacker outputs are appended to `decrypted_snoop_packets.log` by shor_demo.py.
- These logs are for demo/educational quantum-attack simulation only; must NOT be enabled in production.

## 7. Directory & Main Files
- `main.py` — CLI simulation entrypoint
- `app.py` — REST API for frontend or programmatic calls
- `grid/grid.py` — main system logic (ledger, validation, registration)
- `kiosk/kiosk.py` — logic for QR/VFID and transaction relay
- `franchise/franchise.py` — franchise helper logic
- `user/user.py` — user/payment client logic
- `quantum/shor_demo.py` — quantum attack demo (RSA break): see above WARNING about log file
- `blockchain/block.py` — block structure & logic

## 8. Further Reading / References
- [ASCON](https://ascon.iaik.tugraz.at/)
- [SHA-3 Standard](https://keccak.team/keccak.html)
- [Shor's Algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm)
- [Blockchain overview](https://blockchain.com/)

## 9. Security and Privacy Note
- **The snoop_packet.log is maintained for educational demo ONLY. In a real deployment, sensitive keys or ciphertexts should NEVER be logged. All cryptographic demos use intentionally weak keys for vulnerability demonstration.**
- Your passwords/PINs/UIDs are always cryptographically hashed (SHA-3) in simulated storage.
