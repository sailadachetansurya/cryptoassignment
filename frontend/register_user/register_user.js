document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-user-form');
    const statusDisplay = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const mobile = document.getElementById('mobile').value;
        const pin = document.getElementById('pin').value;
        const balance = document.getElementById('balance').value;
        
        statusDisplay.innerHTML = "Registering and hashing credentials...";
        statusDisplay.style.color = "var(--text-primary)";
        statusDisplay.style.display = "block";
        resultDiv.style.display = "none";
        
        const payload = {
            name: name,
            mobile: mobile,
            pin: pin,
            initial_balance: parseFloat(balance)
        };
        
        try {
            const res = await fetch('/api/user/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (res.ok) {
                statusDisplay.style.display = "none";
                resultDiv.style.display = "block";
                document.getElementById('res-uid').textContent = data.uid;
                document.getElementById('res-vmid').textContent = data.vmid;
                form.reset();
            } else {
                statusDisplay.textContent = "Error: " + data.message;
                statusDisplay.style.color = "var(--danger-color)";
            }
        } catch (error) {
            statusDisplay.textContent = "Network Error.";
            statusDisplay.style.color = "var(--danger-color)";
        }
    });
});