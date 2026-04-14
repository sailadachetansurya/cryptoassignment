document.addEventListener("DOMContentLoaded", () => {
  // IDs from current attacker_dashboard/index.html
  const refreshBtn = document.getElementById("refresh-btn");
  const autoRefreshCheckbox = document.getElementById("auto-refresh");
  const pollIntervalSelect = document.getElementById("poll-interval");
  const statusBadge = document.getElementById("status-badge");
  const packetTableBody = document.getElementById("packet-table-body");
  const recoveredPreview = document.getElementById("recovered-preview");

  let pollTimer = null;
  let lastSeenTopTimestamp = null;

  function setStatus(message, type = "info") {
    if (!statusBadge) return;
    statusBadge.textContent = message;

    const colors = {
      info: "var(--text-secondary)",
      success: "var(--success-color, #4caf50)",
      warn: "var(--warning-color, #ff9800)",
      danger: "var(--danger-color, #e53935)",
    };
    statusBadge.style.color = colors[type] || colors.info;
  }

  function safeJson(value) {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }

  function shorten(text, max = 80) {
    const s = String(text ?? "");
    return s.length <= max ? s : `${s.slice(0, max - 1)}…`;
  }

  function escapeAttr(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll('"', "&quot;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  // --- lightweight simulated "attacker" helpers (frontend-side preview) ---
  function gcd(a, b) {
    let x = Math.abs(Number(a));
    let y = Math.abs(Number(b));
    while (y !== 0) {
      const t = y;
      y = x % y;
      x = t;
    }
    return x;
  }

  function modPow(base, exp, mod) {
    let b = BigInt(base) % BigInt(mod);
    let e = BigInt(exp);
    const m = BigInt(mod);
    let result = 1n;
    while (e > 0n) {
      if (e % 2n === 1n) result = (result * b) % m;
      e = e / 2n;
      b = (b * b) % m;
    }
    return result;
  }

  function modInverse(a, m) {
    let t = 0n;
    let newT = 1n;
    let r = BigInt(m);
    let newR = BigInt(a);

    while (newR !== 0n) {
      const q = r / newR;
      [t, newT] = [newT, t - q * newT];
      [r, newR] = [newR, r - q * newR];
    }

    if (r > 1n) {
      throw new Error("Mod inverse does not exist");
    }
    if (t < 0n) t += BigInt(m);
    return t;
  }

  function factorTinyN(n) {
    const N = Number(n);
    if (!Number.isInteger(N) || N <= 1) throw new Error("Invalid n");
    if (N % 2 === 0) return [2, N / 2];

    // Tiny-n brute-force factor for demo
    for (let i = 3; i * i <= N; i += 2) {
      if (N % i === 0) return [i, N / i];
    }
    throw new Error("Failed to factor n");
  }

  function decryptPayloadArray(values, n, d) {
    if (!Array.isArray(values) || values.length === 0) {
      throw new Error("Missing encrypted payload array");
    }
    return values
      .map((v) => {
        if (!Number.isInteger(v)) {
          throw new Error("Encrypted payload contains non-integers");
        }
        const codePoint = Number(modPow(BigInt(v), BigInt(d), BigInt(n)));
        return String.fromCodePoint(codePoint);
      })
      .join("");
  }

  function recoverEntry(entry) {
    const encryptedPayload =
      entry.encrypted_payload ?? entry.ciphertext ?? null;
    const n = Number(entry.n);
    const e = Number(entry.e);

    if (!Array.isArray(encryptedPayload) || encryptedPayload.length === 0) {
      throw new Error(
        "entry.encrypted_payload/ciphertext must be a non-empty list",
      );
    }
    if (!Number.isInteger(n) || !Number.isInteger(e)) {
      throw new Error("entry.n and entry.e must be integers");
    }

    const [p, q] = factorTinyN(n);
    const phi = (p - 1) * (q - 1);
    const d = Number(modInverse(BigInt(e), BigInt(phi)));

    const plaintextRaw = decryptPayloadArray(encryptedPayload, n, d);
    let plaintextJson = null;
    try {
      plaintextJson = JSON.parse(plaintextRaw);
    } catch {
      plaintextJson = null;
    }

    return { p, q, d, plaintextRaw, plaintextJson };
  }

  function buildPreview(entry, recoveryResult, recoveryError) {
    return {
      timestamp: entry.timestamp ?? null,
      packet_type: entry.packet_type ?? null,
      public_key: { n: entry.n ?? null, e: entry.e ?? null },
      meta: entry.meta ?? {},
      ciphertext_length: Array.isArray(entry.encrypted_payload)
        ? entry.encrypted_payload.length
        : Array.isArray(entry.ciphertext)
          ? entry.ciphertext.length
          : null,
      recovered: recoveryResult
        ? {
            p: recoveryResult.p,
            q: recoveryResult.q,
            d: recoveryResult.d,
            plaintext_json: recoveryResult.plaintextJson,
            plaintext_raw: recoveryResult.plaintextRaw,
          }
        : null,
      attack_error: recoveryError ? String(recoveryError) : null,
    };
  }

  function renderEmptyState() {
    packetTableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center; color: var(--text-secondary);">
          No intercepted packets yet.
        </td>
      </tr>
    `;
    recoveredPreview.textContent =
      "Click a row to inspect decrypted payload details.";
  }

  function renderRows(entries) {
    packetTableBody.innerHTML = "";

    if (!Array.isArray(entries) || entries.length === 0) {
      renderEmptyState();
      return;
    }

    const recoveredCache = [];

    entries.forEach((entry, idx) => {
      let recoveryResult = null;
      let recoveryError = null;
      try {
        recoveryResult = recoverEntry(entry);
      } catch (err) {
        recoveryError = err;
      }

      recoveredCache[idx] = { recoveryResult, recoveryError };

      const ts = entry.timestamp
        ? new Date(entry.timestamp).toLocaleString()
        : "—";
      const packetType = entry.packet_type || "unknown";
      const n = entry.n ?? "—";
      const e = entry.e ?? "—";
      const meta = entry.meta ?? {};
      const hasRecovered = !!recoveryResult;

      const tr = document.createElement("tr");
      tr.style.cursor = "pointer";
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td>${ts}</td>
        <td>${packetType}</td>
        <td style="font-family: monospace;">(${n}, ${e})</td>
        <td title="${escapeAttr(safeJson(meta))}">${shorten(safeJson(meta), 70)}</td>
        <td>
          ${
            hasRecovered
              ? "✅ Yes"
              : `<span style="color: var(--danger-color);">⚠ Error</span>`
          }
        </td>
      `;

      tr.addEventListener("click", () => {
        const { recoveryResult: rr, recoveryError: re } = recoveredCache[idx];
        recoveredPreview.textContent = safeJson(buildPreview(entry, rr, re));

        if (
          rr?.plaintextJson &&
          Object.prototype.hasOwnProperty.call(rr.plaintextJson, "pin")
        ) {
          setStatus(`Recovered PIN detected: ${rr.plaintextJson.pin}`, "warn");
        }
      });

      packetTableBody.appendChild(tr);
    });

    // Default preview = newest row
    const first = entries[0];
    const firstRecovery = recoveredCache[0];
    recoveredPreview.textContent = safeJson(
      buildPreview(
        first,
        firstRecovery.recoveryResult,
        firstRecovery.recoveryError,
      ),
    );
  }

  async function fetchPackets() {
    try {
      const res = await fetch("/api/attacker/packets?limit=20");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const entries = Array.isArray(data.entries) ? data.entries : [];
      const logPath = data.snoop_log_path
        ? ` | log: ${data.snoop_log_path}`
        : "";

      renderRows(entries);

      const topTs = entries[0]?.timestamp || null;
      if (topTs && topTs !== lastSeenTopTimestamp) {
        lastSeenTopTimestamp = topTs;
        setStatus(
          `Updated ${new Date().toLocaleTimeString()}${logPath}`,
          "success",
        );
      } else {
        setStatus(
          `Listening ${new Date().toLocaleTimeString()}${logPath}`,
          "info",
        );
      }
    } catch (error) {
      console.error("Attacker dashboard fetch failed:", error);
      setStatus("Failed to fetch attacker packets.", "danger");
    }
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function startPolling() {
    stopPolling();
    const seconds = Math.max(
      0.5,
      Number.parseFloat(pollIntervalSelect?.value || "2"),
    );
    pollTimer = setInterval(fetchPackets, seconds * 1000);
  }

  refreshBtn?.addEventListener("click", fetchPackets);

  autoRefreshCheckbox?.addEventListener("change", () => {
    if (autoRefreshCheckbox.checked) {
      startPolling();
      setStatus("Auto-refresh enabled", "success");
    } else {
      stopPolling();
      setStatus("Auto-refresh paused", "warn");
    }
  });

  pollIntervalSelect?.addEventListener("change", () => {
    if (autoRefreshCheckbox?.checked) {
      startPolling();
      setStatus("Polling interval updated", "info");
    }
  });

  // initial load
  fetchPackets();
  if (autoRefreshCheckbox?.checked) {
    startPolling();
  }
});
