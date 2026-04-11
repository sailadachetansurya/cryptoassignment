document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const qrStringDisplay = document.getElementById('qr-string');
    const statusDisplay = document.getElementById('status');

    async function fetchNewSessionString() {
        qrStringDisplay.textContent = "Encrypting...";
        try {
            const response = await fetch('/api/kiosk/generate_vfid');
            if (!response.ok) {
                throw new Error('Failed to generate session string.');
            }
            const data = await response.json();
            qrStringDisplay.textContent = data.vfid;
            statusDisplay.textContent = "Ready for user input.";
            statusDisplay.style.color = "var(--accent-color)";
        } catch (error) {
            statusDisplay.textContent = "Network Error";
            statusDisplay.style.color = "var(--danger-color)";
        }
    }

    generateBtn.addEventListener('click', fetchNewSessionString);
    
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(qrStringDisplay.textContent);
            copyBtn.textContent = "Copied!";
            setTimeout(() => {
                copyBtn.textContent = "Copy VFID String";
            }, 2000);
        } catch (err) {
            console.error('Failed to copy: ', err);
        }
    });
    
    // Auto-generate on load
    fetchNewSessionString();
});