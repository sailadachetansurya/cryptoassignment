document.addEventListener('DOMContentLoaded', () => {
    // Top-Up User
    const uForm = document.getElementById('add-user-balance-form');
    const uStatus = document.getElementById('u-status');
    
    uForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const vmid = document.getElementById('vmid').value;
        const amount = document.getElementById('u-amount').value;
        
        uStatus.style.display = "block";
        uStatus.innerHTML = "Processing User funding...";
        uStatus.style.color = "var(--text-primary)";
        
        try {
            const res = await fetch('/api/user/add_balance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vmid: vmid, amount: parseFloat(amount) })
            });
            const data = await res.json();
            
            if (res.ok) {
                uStatus.innerHTML = `✅ Successfully funded! New Balance: $${data.new_balance.toFixed(2)}`;
                uStatus.style.color = "var(--success-color)";
                uForm.reset();
            } else {
                uStatus.innerHTML = "❌ Error: " + data.message;
                uStatus.style.color = "var(--danger-color)";
            }
        } catch (error) {
            uStatus.innerHTML = "Network Error.";
            uStatus.style.color = "var(--danger-color)";
        }
    });

    // Top-Up Franchise
    const fForm = document.getElementById('add-franchise-balance-form');
    const fStatus = document.getElementById('f-status');
    
    fForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fid = document.getElementById('fid').value;
        const amount = document.getElementById('f-amount').value;
        
        fStatus.style.display = "block";
        fStatus.innerHTML = "Processing Franchise funding...";
        fStatus.style.color = "var(--text-primary)";
        
        try {
            const res = await fetch('/api/franchise/add_balance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fid: fid, amount: parseFloat(amount) })
            });
            const data = await res.json();
            
            if (res.ok) {
                fStatus.innerHTML = `✅ Successfully funded! New Balance: $${data.new_balance.toFixed(2)}`;
                fStatus.style.color = "var(--success-color)";
                fForm.reset();
            } else {
                fStatus.innerHTML = "❌ Error: " + data.message;
                fStatus.style.color = "var(--danger-color)";
            }
        } catch (error) {
            fStatus.innerHTML = "Network Error.";
            fStatus.style.color = "var(--danger-color)";
        }
    });
});