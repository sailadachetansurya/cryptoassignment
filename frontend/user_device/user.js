document.getElementById('payment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const kioskString = document.getElementById('kiosk-string').value;
    const vmid = document.getElementById('vmid').value;
    const amount = document.getElementById('amount').value;
    const pin = document.getElementById('pin').value;
    const statusDisplay = document.getElementById('status');

    statusDisplay.textContent = "RSA Encrypting and contacting Grid...";
    statusDisplay.style.color = "var(--text-primary)";

    const payload = {
        vfid_string: kioskString,
        vmid: vmid,
        amount: parseFloat(amount),
        pin: pin // NOTE: Backend will simulate RSA encryption/Shor's interception here
    };

    try {
        // BACKEND LINK: Replace URL with your actual Python API endpoint
        /*
        const response = await fetch('http://localhost:5000/api/user/authorize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        */

        // Simulated API Delay
        setTimeout(() => {
            console.log("Sent Payload:", payload);
            statusDisplay.textContent = "Payment Authorized. Charging Started!";
            statusDisplay.style.color = "var(--accent-color)";
        }, 800);

    } catch (error) {
        statusDisplay.textContent = "Transaction Failed. See Console.";
        statusDisplay.style.color = "var(--danger-color)";
        console.error("Payment error:", error);
    }
});