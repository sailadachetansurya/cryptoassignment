document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('franchise-form');
    const status = document.getElementById('status');
    const qrPayload = document.getElementById('qr-payload');
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
                tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-secondary)">No franchises found.</td></tr>';
                return;
            }

            franchises.forEach((row) => {
                tableBody.innerHTML += `
                    <tr>
                        <td style="font-family: monospace;">${row.fid}</td>
                        <td>${row.name}</td>
                        <td>${row.zone}</td>
                        <td>$${Number(row.balance).toFixed(2)}</td>
                    </tr>
                `;
            });
        } catch (error) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--danger-color)">Failed to load franchise list.</td></tr>';
        }
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const payload = {
            provider: document.getElementById('provider').value.trim(),
            name: document.getElementById('name').value.trim(),
            zone_code: document.getElementById('zone').value.trim(),
            password: document.getElementById('password').value,
            initial_balance: Number(document.getElementById('balance').value),
        };

        status.textContent = 'Registering franchise...';
        status.style.color = 'var(--text-primary)';

        try {
            const response = await fetch('/api/franchise/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || 'Franchise registration failed.');
            }

            qrPayload.textContent = result.qr_payload;
            status.textContent = `Franchise registered. FID: ${result.fid}`;
            status.style.color = 'var(--accent-color)';
            await loadFranchises();
        } catch (error) {
            status.textContent = error.message;
            status.style.color = 'var(--danger-color)';
        }
    });

    refreshBtn.addEventListener('click', loadFranchises);
    loadFranchises();
});
