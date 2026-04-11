document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refresh-btn');
    const tableBody = document.getElementById('franchise-table-body');

    async function loadFranchises() {
        try {
            const response = await fetch('/api/franchise/list');
            if (!response.ok) {
                throw new Error('Failed to load franchises');
            }
            const franchises = await response.json();
            tableBody.innerHTML = '';

            if (franchises.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-secondary)">No franchises found.</td></tr>';
                return;
            }

            franchises.forEach((row) => {
                tableBody.innerHTML += `
                    <tr>
                        <td style="font-family: monospace; font-size: 0.85em;">${row.fid}</td>
                        <td>${row.name}</td>
                        <td>${row.provider || 'N/A'}</td>
                        <td>${row.zone}</td>
                        <td style="color: var(--success-color); font-weight: bold;">$${Number(row.balance).toFixed(2)}</td>
                    </tr>
                `;
            });
        } catch (error) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--danger-color)">Failed to load franchise list.</td></tr>';
        }
    }

    refreshBtn.addEventListener('click', loadFranchises);
    
    // Initial load
    loadFranchises();
});
