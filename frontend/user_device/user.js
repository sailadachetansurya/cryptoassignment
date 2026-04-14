document.addEventListener('DOMContentLoaded', () => {
    const amountInput = document.getElementById('amount');
    const estKwhDisplay = document.getElementById('est-kwh');
    const rateDisplay = document.getElementById('rate');
    const RATE_PER_KWH = 0.45; // Simulated cost per kWh (EV "litres" equivalent)
    
    rateDisplay.textContent = RATE_PER_KWH.toFixed(2);
    
    amountInput.addEventListener('input', () => {
        const amt = parseFloat(amountInput.value);
        if(!isNaN(amt) && amt > 0) {
            estKwhDisplay.textContent = (amt / RATE_PER_KWH).toFixed(2);
        } else {
            estKwhDisplay.textContent = "0.00";
        }
    });
});

function modPow(base, exponent, modulus) {
    if (modulus === 1n) {
        return 0n;
    }
    let result = 1n;
    let b = base % modulus;
    let e = exponent;
    while (e > 0n) {
        if (e % 2n === 1n) {
            result = (result * b) % modulus;
        }
        e = e / 2n;
        b = (b * b) % modulus;
    }
    return result;
}

function rsaEncryptText(plainText) {
    // Toy RSA parameters used only for simulation in this project.
    const n = 3233n;
    const e = 17n;
    return Array.from(plainText).map((ch) => {
        const m = BigInt(ch.codePointAt(0));
        return Number(modPow(m, e, n));
    });
}

document.getElementById('payment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const kioskString = document.getElementById('kiosk-string').value;
    const vmid = document.getElementById('vmid').value;
    const amount = document.getElementById('amount').value;
    const pin = document.getElementById('pin').value;
    const statusDisplay = document.getElementById('status');

    // Simulate RSA encryption before transfer to the backend.
    statusDisplay.innerHTML = "RSA Encrypting credentials...<br>Contacting Grid...";
    statusDisplay.style.color = "var(--text-primary)";

    const amountNumber = parseFloat(amount);
    if (Number.isNaN(amountNumber) || amountNumber <= 0) {
        statusDisplay.textContent = "Enter a valid positive amount.";
        statusDisplay.style.color = "var(--danger-color)";
        return;
    }

    const clearPayload = JSON.stringify({
        vmid: vmid,
        pin: pin,
        amount: amountNumber,
        vfid: kioskString
    });

    const payload = {
        vfid_string: kioskString,
        encrypted_payload: rsaEncryptText(clearPayload)
    };

    try {
        const response = await fetch('/api/user/authorize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || 'Authorization request failed.');
        }

        statusDisplay.textContent = result.message;
        statusDisplay.style.color = result.approved ? "var(--accent-color)" : "var(--danger-color)";

    } catch (error) {
        statusDisplay.textContent = error.message || "Transaction Failed. See Console.";
        statusDisplay.style.color = "var(--danger-color)";
        console.error("Payment error:", error);
    }
});