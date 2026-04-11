document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refresh-btn');
    const ledgerBody = document.getElementById('ledger-body');
    const simStatus = document.getElementById('sim-status');
    const btnActivate = document.getElementById('btn-activate');
    const btnDeactivate = document.getElementById('btn-deactivate');
    const machineFailToggle = document.getElementById('machine-fail-toggle');

    function showStatus(message, isSuccess = true) {
        simStatus.style.display = "block";
        simStatus.textContent = message;
        simStatus.style.color = isSuccess ? "var(--success-color)" : "var(--danger-color)";
        setTimeout(() => simStatus.style.display = "none", 5000);
    }

    async function fetchLedger() {
        refreshBtn.textContent = "Refreshing...";
        
        try {
            const response = await fetch('/api/grid/ledger');
            if (!response.ok) {
                throw new Error('Failed to fetch ledger.');
            }

            const blocks = await response.json();
            ledgerBody.innerHTML = '';

            if (blocks.length === 0) {
                ledgerBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-secondary)">No blocks yet.</td></tr>';
            } else {
                blocks.forEach(block => {
                    const displayStatus = block.dispute_or_refund_flag ? `${block.status} (Dispute/Refund)` : block.status;
                    const statusClass = displayStatus.includes('Success') ? 'success' : 'fail';
                    // We also show the raw transaction hash so they can copy it for Refund tests
                    ledgerBody.innerHTML += `
                        <tr>
                            <td>${new Date(block.time).toLocaleString()}</td>
                            <td style="font-family: monospace; font-size: 0.85em;">${block.hash}</td>
                            <td style="font-weight: bold; color: ${block.amount < 0 ? 'var(--danger-color)' : 'var(--text-primary)'};">$${block.amount}</td>
                            <td class="${statusClass}">${displayStatus}</td>
                        </tr>
                    `;
                });
            }

            refreshBtn.textContent = "Refresh Data";

        } catch (error) {
            console.error("Failed to fetch ledger", error);
            refreshBtn.textContent = "Error!";
        }
    }

    btnDeactivate.addEventListener('click', async (e) => {
        e.preventDefault();
        const vmid = document.getElementById('vmid-status').value;
        const res = await fetch('/api/user/close', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vmid })
        });
        const data = await res.json();
        const ok = res.status === 200;
        showStatus(data.message || data.error, ok);
        if (ok) document.getElementById('vmid-status').value = '';
    });

    btnActivate.addEventListener('click', async (e) => {
        e.preventDefault();
        const vmid = document.getElementById('vmid-status').value;
        const res = await fetch('/api/user/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vmid })
        });
        const data = await res.json();
        const ok = res.status === 200;
        showStatus(data.message || data.error, ok);
        if (ok) document.getElementById('vmid-status').value = '';
    });

    machineFailToggle.addEventListener('change', async (e) => {
        const isFailing = e.target.checked;
        try {
            const res = await fetch('/api/kiosk/simulate_failure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fail: isFailing })
            });
            const data = await res.json();
            if (data.ok) {
                showStatus(`Kiosk Hardware Failure Mode: ${data.simulate_machine_failure ? 'ON' : 'OFF'}`, !data.simulate_machine_failure);
            }
        } catch(err) {
            console.error(err);
        }
    });

    refreshBtn.addEventListener('click', fetchLedger);
    
    // Initial fetch
    fetchLedger();
});