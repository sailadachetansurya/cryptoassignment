document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-franchise-form');
    const statusDisplay = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const provider = document.getElementById('provider').value;
        const zone = document.getElementById('zone').value;
        const password = document.getElementById('password').value;
        const balance = document.getElementById('balance').value;
        
        statusDisplay.innerHTML = "Registering with Grid Authority... hashing Password & verifying Zone code...";
        statusDisplay.style.color = "var(--text-primary)";
        statusDisplay.style.display = "block";
        resultDiv.style.display = "none";
        
        const payload = {
            name: name,
            provider: provider,
            zone_code: zone,
            password: password,
            initial_balance: parseFloat(balance)
        };
        
        try {
            const res = await fetch('/api/franchise/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (res.ok) {
                statusDisplay.style.display = "none";
                resultDiv.style.display = "block";
                document.getElementById('res-fid').textContent = data.fid;
                form.reset();
            } else {
                statusDisplay.textContent = "Validation Failed: " + data.message;
                statusDisplay.style.color = "var(--danger-color)";
            }
        } catch (error) {
            statusDisplay.textContent = "Network Error.";
            statusDisplay.style.color = "var(--danger-color)";
        }
    });
});