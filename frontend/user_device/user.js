document.getElementById('payment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const kioskString = document.getElementById('kiosk-string').value;
    const vmid = document.getElementById('vmid').value;
    const amount = document.getElementById('amount').value;
    const pin = document.getElementById('pin').value;
    const statusDisplay = document.getElementById('status');

    statusDisplay.textContent = "Contacting Grid...";
    statusDisplay.style.color = "var(--text-primary)";

    const payload = {
        vfid_string: kioskString,
        vmid: vmid,
        amount: parseFloat(amount),
        pin: pin
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