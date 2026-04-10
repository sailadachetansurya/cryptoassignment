document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const qrStringDisplay = document.getElementById('qr-string');
    const statusDisplay = document.getElementById('status');

    // Simulate calling the backend to get the ASCON encrypted VFID
    async function fetchNewSessionString() {
        qrStringDisplay.textContent = "Encrypting...";
        try {
            // BACKEND LINK: Replace URL with your actual Python API endpoint
            // const response = await fetch('http://localhost:5000/api/kiosk/generate_vfid');
            // const data = await response.json();
            // qrStringDisplay.textContent = data.vfid;

            // Simulated response for now
            setTimeout(() => {
                const simulatedVFID = "ASCON-" + Math.floor(Math.random() * 100000) + "-TIMESTAMP-" + Date.now().toString().slice(-6);
                qrStringDisplay.textContent = simulatedVFID;
                statusDisplay.textContent = "Ready for user input.";
                statusDisplay.style.color = "var(--accent-color)";
            }, 500);
        } catch (error) {
            statusDisplay.textContent = "Network Error";
            statusDisplay.style.color = "var(--danger-color)";
        }
    }

    generateBtn.addEventListener('click', fetchNewSessionString);
    
    // Auto-generate on load
    fetchNewSessionString();
});