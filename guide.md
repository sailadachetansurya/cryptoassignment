# EV Charging Payment Gateway Guide

## 1. Purpose
This guide translates the term-project PDF into a clear implementation document for a secure, centralized EV charging payment simulation.

The project combines:
- Lightweight cryptography (ASCON)
- SHA-3 based identity and transaction hashing
- A centralized blockchain ledger
- A quantum-vulnerability demonstration using Shor's algorithm on RSA

## 2. Scope and Architecture
### 2.1 Physical Components (Build These)
1. Charging Kiosk
2. User Device (client)
3. Grid Authority system

### 2.2 Participating Entities (Model These)
1. Grid Authority
2. Franchise
3. EV Owner
4. Charging Kiosk

Note: The PDF describes 3 physical devices and 4 logical entities. Your simulation should reflect both views.

## 3. Privacy and Security Intent
- Protect user credentials and prevent payment fraud.
- Keep billing records tamper-evident using blockchain chaining.
- Treat kiosk-side scanned payload as untrusted input.
- Do not use QR for location disclosure. Use FID to map location server-side if needed.

## 4. Edge Cases & Documented Assumptions
As per the project requirements, the system natively handles practical edge cases, governed by the following assumptions:

### 4.1 Account Closure Mid-Session
- **Scenario:** The user initiates an EV charging session at a kiosk, but their EV Owner Account gets deactivated or closed before authorization completes.
- **Assumption:** We assume the Grid Authority performs a real-time validation of the account's active status at the exact moment of transaction processing. If the `active` flag evaluates to `False`, the transaction is strictly rejected (`ACCOUNT_CLOSED`) before any value is exchanged or any block is mined.

### 4.2 Insufficient Balance During Transaction
- **Scenario:** The EV Owner authorizes a payment amount that exceeds their current wallet balance.
- **Assumption:** We assume transactions are processed atomically. The Grid Authority checks the user's available balance right when the transaction is received. If the requested amount is strictly greater than the balance, it is instantly rejected (`INSUFFICIENT_BALANCE`) and the charging kiosk is notified to reject the plug.

### 4.3 Hardware Failure After Successful Payment
- **Scenario:** The payment fully succeeds, the block is mined, and the franchise receives the funds—but the actual kiosk hardware subsequently fails to dispense electricity.
- **Assumption:** We assume that blockchains must remain strictly immutable. Therefore, failed deliveries must be reported to the Grid Authority (the central arbiter) which then initiates a **Refund Transaction**. Instead of modifying or deleting the old block, the Grid appends a brand *new* block mapping the funds back to the user, marked specifically with a `dispute_or_refund_flag` set to `True`. This ensures financial accuracy while preserving a perfectly honest, cryptographically linked audit trail.

## 4. Registration and Setup Flow
Registration is one-time and happens before charging transactions.

### 4.1 Grid Registration
Initialize provider/zone mapping in the grid, as described in the PDF:
- 3 central energy providers
- 3 regional zones per provider

### 4.2 Franchise Registration
Franchise provides:
- Franchise name
- Zone code
- Password
- Initial account balance

Grid generates:
- FID (16-digit hexadecimal identifier)
- Derivation basis: SHA-3 (Keccak-256) over franchise data including creation time and password

### 4.3 User Registration
User provides:
- User/account details required by your implementation
- PIN for authorization

Grid generates:
- UID (16-digit identifier)

User then creates:
- VMID using UID + mobile number (as required by the PDF)

Grid stores at minimum:
- UID
- VMID
- PIN reference (stored securely)
- Balance

## 5. Transaction Flow (End-to-End)
1. Kiosk encrypts station identity data and displays QR payload.
2. EV Owner scans QR.
3. EV Owner enters VMID, PIN, and charging amount.
4. User device sends request to kiosk.
5. Kiosk decrypts QR payload to recover station identity.
6. Kiosk validates identity consistency for this station.
7. Kiosk forwards authorization request to Grid Authority.
8. Grid validates VMID, PIN, and available funds.
9. If valid, grid records blockchain transaction and transfers funds to franchise account.
10. Grid returns approve/reject response.
11. Kiosk displays status and unlocks/continues charging only on approval.

### 5.1 Why Kiosk Decrypts QR
This step is necessary to prevent tampered or replayed client payloads.
It ensures the request is bound to the correct station before forwarding to grid.

## 6. Cryptography Requirements
### 6.1 SHA-3 (Keccak-256)
Use for:
- UID/FID derivation
- Transaction ID generation
- Optional integrity hashes

### 6.2 ASCON (Lightweight Cryptography)
Use for:
- Encrypting station identity payload in QR
- Decrypting at kiosk during transaction processing

The PDF also mentions dynamic VFID style behavior based on FID and timestamp. You can model this as a rotating encrypted station token if desired.

## 7. Quantum Security Demonstration
Implement a simple, scoped demo:
- Show that RSA-based key exchange is vulnerable in principle to Shor's algorithm.
- Demonstration only; no production-grade quantum pipeline required.

## 8. Blockchain Requirements
Maintain a centralized ledger at the grid.

Each valid transaction appends one block with at least:
- transaction_id (SHA-3 of UID, FID, timestamp, amount)
- previous_hash
- timestamp
- dispute_or_refund_flag (boolean)

Support a reverse/refund transaction path for cases like payment success but charging hardware failure.

## 9. Edge Cases and Assumptions
Document assumptions explicitly. Handle reasonable edge cases, such as:
1. Wrong PIN
2. Insufficient balance
3. Account closure mid-session
4. Hardware failure after successful payment (requires refund/reversal block)
5. QR/station identity mismatch

## 10. Out of Scope
Do not overbuild beyond project needs:
- Full mobile app production stack
- Real-world distributed blockchain network
- Full quantum computing implementation
- Hardware-grade QR/camera integration

## 11. Minimum Working Deliverable
Your CLI simulation should demonstrate:
1. Grid, franchise, and user registration
2. QR/token generation with ASCON-based encryption
3. VMID/PIN/amount transaction initiation
4. Grid authorization and balance transfer
5. Blockchain block append
6. Failure handling for key edge cases
7. A basic Shor-vulnerability demonstration narrative or toy simulation

## 12. Suggested Folder Structure
```text
project/
|-- grid/
|   `-- grid.py
|-- kiosk/
|   `-- kiosk.py
|-- user/
|   `-- user.py
|-- crypto/
|   |-- ascon.py
|   `-- sha3.py
|-- blockchain/
|   `-- block.py
|-- quantum/
|   `-- shor_demo.py
`-- main.py
```

## 13. Submission Notes (From PDF)
- Submit source code + README in one .zip or .tar file.
- Use required naming format (team-based) from the course instructions.
- README should include project summary, run steps, and team members.

## 14. One-Line Summary
Scan encrypted station QR, submit VMID/PIN/amount, verify at kiosk and grid, settle funds, and record immutable transaction data with refund support.
