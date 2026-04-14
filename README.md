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

3. **Quantum Cryptography Demo (Shor's RSA break):**
   ```
   python quantum/shor_demo.py
   ```
   This simulates Shor's algorithm factoring a small RSA public-key exchange and shows plaintext extraction from the cipher, demonstrating classical crypto broken by quantum algorithms.

## 5. Core Features & Technologies
- **ASCON LWC**: Franchise IDs and payment QR/VFID payloads are encrypted using ASCON (to simulate real LWC on constrained kiosks).
- **SHA-3/Keccak Hashing**: Used for UID, FID, VMID, and block IDs; all transaction/integrity hashes.
- **Blockchain Ledger**: Every valid transaction is stored in an immutable, tamper-evident chain. Each block includes: txn ID, previous hash, amount, timestamp, and dispute/refund flags (for chargebacks or hardware issues).
- **Quantum Crypto Simulation**: Our code includes a purely classical Shor's attack demo on toy RSA, per the spec. This highlights vulnerability of classical keys to quantum attacks.

## 6. Edge Cases & Design Assumptions
- *Account can be closed* mid-session; deactivated accounts are rejected for new transactions.
- *Insufficient funds* and *invalid PIN/VMID* are handled fast-fail style.
- *Hardware failure/disputes*: A special flag allows simulating kiosk dispense failure; upon activation, a refund/reversal block is appended, and balances are corrected.
- All entities are managed in-memory, single-system for simulation: Grid Authority, Franchise, User/EV Owner, Charging Kiosk.
- For demo, QR code payload is a string (encrypted); displaying as image/QR can be added easily (not asked in the handout).

## 7. Directory & Main Files
- `main.py` — CLI simulation entrypoint
- `app.py` — REST API for frontend or programmatic calls
- `grid/grid.py` — main system logic (ledger, validation, registration)
- `kiosk/kiosk.py` — logic for QR/VFID and transaction relay
- `franchise/franchise.py` — franchise helper logic
- `user/user.py` — user/payment client logic
- `quantum/shor_demo.py` — quantum attack demo (RSA break)
- `blockchain/block.py` — block structure & logic

## 8. Further Reading / References
- [ASCON](https://ascon.iaik.tugraz.at/)
- [SHA-3 Standard](https://keccak.team/keccak.html)
- [Shor's Algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm)
- [Blockchain overview](https://blockchain.com/)

## 9. Submission Info
ZIP/tar as `BITSF463_Team_4.zip` or `.tar`.

For doubts contact:
TAs: Ashmik Harinkhede (h20250037@hyderabad.bits-pilani.ac.in), Harsh Patel (h20250179@hyderabad.bits-pilani.ac.in), Kritii Gupta (f20220757@hyderabad.bits-pilani.ac.in)

*Deadline: 11:59 PM, April 14th, 2026.*
