document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refresh-btn');
    const ledgerBody = document.getElementById('ledger-body');

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
                    ledgerBody.innerHTML += `
                        <tr>
                            <td>${block.time}</td>
                            <td style="font-family: monospace;">${block.hash}</td>
                            <td>${block.amount}</td>
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

    refreshBtn.addEventListener('click', fetchLedger);
    
    // Initial fetch
    fetchLedger();
});