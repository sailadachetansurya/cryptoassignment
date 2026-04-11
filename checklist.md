# EV Charging Payment Gateway - Integration & Edge Cases Checklist

## 1. Grid Pre-Registration (Backend Setup) 🏢
- [x] **Seed EV Owners & Franchises**: Read fixed franchises and existing EV Owners from a CSV (`franchises.csv` and `users.csv`). Passwords and PINs are securely stored globally as SHA-3 (Keccak-256) hashes. *DONE!*

## 1.5 Refactoring Grid Authority VFID Ownership 🔐
- [x] **Grid ASCON Integration**: Add `generate_vfid(fid)` and `decrypt_vfid(qr_string)` to `grid.py` so the *Grid* acts as the single source of truth for encrypting/decrypting the session string, passing the original FID and timestamp via ASCON.
- [x] **Kiosk simplification**: Update `kiosk.py` to stop generating the QR code locally, and instead request it from the Grid.
- [x] **Payment Flow Fix**: Update `app.py` & `grid.py` to process transactions using the encrypted VFID, forcing the Grid itself to decrypt and validate it. *DONE!*

## 2. Kiosk Frontend Integration 🔌
- [x] **VFID Generation (Kiosk using LWC)**: Franchises (and their FIDs) are pre-registered in the system. The Kiosk uses its assigned FID and encrypts it using ASCON (LWC) to create a dynamic Virtual Franchise ID (VFID). *DONE in `app.py`*
- [x] **Kiosk Session Display**: Connected `frontend/kiosk/kiosk.js` to fetch this ASCON-encrypted VFID string and display it on the screen for the EV Owner to copy. *DONE in `kiosk.js`!*

## 3. EV Owner Frontend Integration 📱
- [x] **Payment Submission**: Update `frontend/user_device/user.js` (representing the EV Owner) to send the copied ASCON string (VFID), VMID, PIN, and Amount via `POST /api/user/authorize`. *DONE!*
- [ ] **RSA / Shor's Algorithm Interception**: Before the backend Grid validates the PIN, simulate sending it via RSA and use Shor's Algorithm to "break" it, demonstrating the quantum vulnerability.

## 4. Grid Validation & Blockchain ⚡
- [x] **Grid Authentication**: Ensure the grid correctly decrypts the ASCON string back to the FID, and verifies the EV Owner's VMID, hashed PIN, and account balance. *DONE!*
- [x] **Blockchain Mining**: Once validated, ensure the transaction is hashed (SHA-3) and mined into the Grid's central blockchain. *DONE!*
- [x] **Franchise/Grid UI Updates**: Connect `frontend/grid_dashboard/grid.js` to `GET /api/grid/ledger` so it live-updates with pass/fail results and the newly mined blocks. *DONE!*
- [ ] **Handle Edge Cases**: Hook up the UI for triggering the Refund/Dispute process (Hardware Dispense Failures) from the Grid Dashboard.