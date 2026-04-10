document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refresh-btn');
    const ledgerBody = document.getElementById('ledger-body');

    async function fetchLedger() {
        refreshBtn.textContent = "Refreshing...";
        
        try {
            // BACKEND LINK: Replace URL with your actual Python API endpoint
            // const response = await fetch('http://localhost:5000/api/grid/ledger');
            // const blocks = await response.json();
            
            // Simulated Data
            setTimeout(() => {
                const simulatedBlocks = [
                    { time: new Date().toLocaleTimeString(), hash: "0x3a9b...f12e", amount: "$25.00", status: "Success" },
                    { time: new Date(Date.now() - 60000).toLocaleTimeString(), hash: "0x89ab...cdef", amount: "$15.00", status: "Failed (Invalid PIN)" },
                ];

                ledgerBody.innerHTML = '';
                simulatedBlocks.forEach(block => {
                    const statusClass = block.status.includes('Success') ? 'success' : 'fail';
                    ledgerBody.innerHTML += `
                        <tr>
                            <td>${block.time}</td>
                            <td style="font-family: monospace;">${block.hash}</td>
                            <td>${block.amount}</td>
                            <td class="${statusClass}">${block.status}</td>
                        </tr>
                    `;
                });
                refreshBtn.textContent = "Refresh Data";
            }, 400);

        } catch (error) {
            console.error("Failed to fetch ledger", error);
            refreshBtn.textContent = "Error!";
        }
    }

    refreshBtn.addEventListener('click', fetchLedger);
    
    // Initial fetch
    fetchLedger();
});