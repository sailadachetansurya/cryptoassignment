import { rsaEncryptText } from "../crypto/rsa.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-franchise-form");
  const statusDisplay = document.getElementById("status");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const provider = document.getElementById("provider").value.trim();
    const zone = document.getElementById("zone").value.trim();
    const password = document.getElementById("password").value;
    const balanceRaw = document.getElementById("balance").value;

    const initialBalance = parseFloat(balanceRaw);
    if (
      !name ||
      !provider ||
      !zone ||
      !password ||
      Number.isNaN(initialBalance) ||
      initialBalance < 0
    ) {
      statusDisplay.textContent =
        "Please provide valid name, provider, zone, password, and non-negative balance.";
      statusDisplay.style.color = "var(--danger-color)";
      statusDisplay.style.display = "block";
      resultDiv.style.display = "none";
      return;
    }

    statusDisplay.innerHTML =
      "Encrypting registration payload with Grid public key...";
    statusDisplay.style.color = "var(--text-primary)";
    statusDisplay.style.display = "block";
    resultDiv.style.display = "none";

    const clearPayload = JSON.stringify({
      name,
      provider,
      zone_code: zone,
      password,
      initial_balance: initialBalance,
    });

    const encryptedPayload = rsaEncryptText(clearPayload);

    try {
      const res = await fetch("/api/franchise/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          encrypted_payload: encryptedPayload,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        statusDisplay.style.display = "none";
        resultDiv.style.display = "block";
        document.getElementById("res-fid").textContent = data.fid;
        form.reset();
      } else {
        statusDisplay.textContent = "Validation Failed: " + data.message;
        statusDisplay.style.color = "var(--danger-color)";
      }
    } catch (error) {
      statusDisplay.textContent = "Network Error.";
      statusDisplay.style.color = "var(--danger-color)";
      console.error("Franchise registration error:", error);
    }
  });
});
