import { rsaEncryptText } from "../crypto/rsa.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-user-form");
  const statusDisplay = document.getElementById("status");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const mobile = document.getElementById("mobile").value.trim();
    const pin = document.getElementById("pin").value.trim();
    const balance = document.getElementById("balance").value;

    statusDisplay.innerHTML = "Encrypting registration payload with RSA...";
    statusDisplay.style.color = "var(--text-primary)";
    statusDisplay.style.display = "block";
    resultDiv.style.display = "none";

    const initialBalance = parseFloat(balance);
    if (!mobile || !pin) {
      statusDisplay.textContent = "Error: mobile and pin are required.";
      statusDisplay.style.color = "var(--danger-color)";
      return;
    }
    if (Number.isNaN(initialBalance) || initialBalance < 0) {
      statusDisplay.textContent =
        "Error: initial balance must be 0 or greater.";
      statusDisplay.style.color = "var(--danger-color)";
      return;
    }

    const clearPayload = JSON.stringify({
      name,
      mobile,
      pin,
      initial_balance: initialBalance,
    });

    const encryptedPayload = rsaEncryptText(clearPayload);

    const payload = {
      encrypted_payload: encryptedPayload,
    };

    try {
      const res = await fetch("/api/user/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        statusDisplay.style.display = "none";
        resultDiv.style.display = "block";
        document.getElementById("res-uid").textContent = data.uid;
        document.getElementById("res-vmid").textContent = data.vmid;
        form.reset();
      } else {
        statusDisplay.textContent =
          "Error: " + (data.message || "Registration failed");
        statusDisplay.style.color = "var(--danger-color)";
      }
    } catch (error) {
      statusDisplay.textContent = "Network Error.";
      statusDisplay.style.color = "var(--danger-color)";
      console.error("User registration error:", error);
    }
  });
});
