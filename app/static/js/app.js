/**
 * Cloud Storage Architecture & Performance Benchmark Studio
 * Client Performance Telemetry & Architectural Visualization Engine
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  let currentOption = 2; // Default to Option 2 to showcase target state
  let activeRecordId = null;
  let allRecords = [];
  let currentFilter = "";

  const metricsHistory = {
    option1: [],
    option2: []
  };

  // DOM Elements - Selection & Navigation
  const optionSelect = document.getElementById("storage-option-select");
  const chipEnvDev = document.getElementById("chip-env-dev");
  const chipEnvProd = document.getElementById("chip-env-prod");
  const pillDb = document.getElementById("pill-db");
  const pillStorage = document.getElementById("pill-storage");

  // Workflow Diagram Elements
  const flowArrowText2 = document.getElementById("flow-arrow-text-2");
  const flowDbTitle = document.getElementById("flow-db-title");
  const flowDbSub = document.getElementById("flow-db-sub");
  const flowStorageTitle = document.getElementById("flow-storage-title");
  const stepStorageTarget = document.getElementById("step-storage-target");
  const stepDbTarget = document.getElementById("step-db-target");

  // Table Elements
  const tableBody = document.getElementById("table-body");
  const tableSearch = document.getElementById("table-search");
  const recordCountSpan = document.getElementById("record-count");
  const thPath = document.getElementById("th-path");
  const tableSubtitle = document.getElementById("table-subtitle");
  const footerStrategyBadge = document.getElementById("footer-strategy-badge");
  const btnRefresh = document.getElementById("btn-refresh");

  // Canvas / Viewport Elements
  const canvasIdleState = document.getElementById("canvas-idle-state");
  const canvasLoadingState = document.getElementById("canvas-loading-state");
  const canvasDisplay = document.getElementById("canvas-display");
  const renderedImage = document.getElementById("rendered-image");
  const rendererSubtitle = document.getElementById("renderer-subtitle");
  const renderControls = document.getElementById("render-controls");
  const btnOpenFull = document.getElementById("btn-open-full");

  // Metadata Tags on Canvas
  const metaValName = document.getElementById("meta-val-name");
  const metaValSize = document.getElementById("meta-val-size");
  const metaValSource = document.getElementById("meta-val-source");

  // Telemetry HUD Elements
  const kpiBigNumber = document.getElementById("kpi-big-number");
  const kpiStatusChip = document.getElementById("kpi-status-chip");
  const telServer = document.getElementById("tel-server");
  const telClient = document.getElementById("tel-client");
  const telPayload = document.getElementById("tel-payload");
  const telBarServer = document.getElementById("tel-bar-server");
  const telBarClient = document.getElementById("tel-bar-client");
  const telBarPayload = document.getElementById("tel-bar-payload");


  // Modals & Buttons
  const btnSeed = document.getElementById("btn-seed");
  const btnOpenArch = document.getElementById("btn-open-arch");
  const modalArch = document.getElementById("modal-arch");
  const btnCloseArch = document.getElementById("btn-close-arch");

  const btnOpenUpload = document.getElementById("btn-open-upload");
  const modalUpload = document.getElementById("modal-upload");
  const btnCloseUpload = document.getElementById("btn-close-upload");
  const btnCancelUpload = document.getElementById("btn-cancel-upload");
  const uploadForm = document.getElementById("upload-form");

  // ==========================================================================
  // System Configuration Loader
  // ==========================================================================
  async function loadSystemConfig() {
    try {
      const res = await fetch("/api/config");
      if (res.ok) {
        const data = await res.json();
        pillDb.textContent = data.database_type.toUpperCase();
        pillStorage.textContent = data.storage_provider.toUpperCase();
        updateFlowVisualizer();
      }
    } catch (err) {
      console.warn("Could not load system config:", err);
    }
  }

  // ==========================================================================
  // Flow Diagram Architecture Visualizer Update
  // ==========================================================================
  function updateFlowVisualizer() {
    if (currentOption === 1) {
      // Option 1: Database BLOB (Heavy DB, All in One)
      flowArrowText2.textContent = "Heavy BLOB Binary Query";
      flowDbTitle.textContent = pillDb.textContent || "Cloud SQL";
      flowDbSub.textContent = "Metadata + Raw BLOB";
      stepStorageTarget.style.display = "none";
      stepDbTarget.style.borderColor = "var(--accent-amber)";
      stepDbTarget.style.background = "#fffbeb";

      tableSubtitle.textContent = "Option 1: Metadata catalog (BLOBs omitted for query performance)";
      footerStrategyBadge.textContent = "Database BLOB Stream";
      footerStrategyBadge.style.color = "var(--accent-amber)";
      footerStrategyBadge.style.background = "#fef3c7";
    } else {
      // Option 2: Hybrid Object Storage
      flowArrowText2.textContent = "Metadata + Direct Bucket Stream";
      flowDbTitle.textContent = pillDb.textContent || "Cloud SQL";
      flowDbSub.textContent = "Lean Metadata Only";
      flowStorageTitle.textContent = `${pillStorage.textContent || 'GCS'} Bucket`;
      stepStorageTarget.style.display = "block";
      stepDbTarget.style.borderColor = "var(--border-light)";
      stepDbTarget.style.background = "#ffffff";

      tableSubtitle.textContent = "Option 2: Lean Metadata + Cloud Object Storage URI";
      footerStrategyBadge.textContent = "Cloud Object Stream";
      footerStrategyBadge.style.color = "var(--accent-emerald)";
      footerStrategyBadge.style.background = "#ecfdf5";
    }
  }

  // ==========================================================================
  // Metadata Catalog Loader (Saroj's Directive: Never fetch BLOBs in table)
  // ==========================================================================
  async function loadTableCatalog() {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6" class="empty-cell">
          <div class="loading-spinner"></div>
          <span>Streaming metadata records from ${currentOption === 1 ? 'Relational DB' : 'Object Store Catalog'}...</span>
        </td>
      </tr>
    `;
    recordCountSpan.textContent = "Querying...";
    thPath.style.display = currentOption === 2 ? "table-cell" : "none";

    try {
      const res = await fetch(`/api/records?option=${currentOption}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      allRecords = await res.json();
      renderTableRows();
    } catch (err) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" class="empty-cell" style="color: var(--accent-rose);">
            <strong>Failed to retrieve metadata catalog:</strong> ${err.message}
          </td>
        </tr>
      `;
      recordCountSpan.textContent = "Error";
    }
  }

  function renderTableRows() {
    const filter = currentFilter.trim().toLowerCase();
    const filtered = allRecords.filter(r => 
      r.name.toLowerCase().includes(filter) ||
      (r.img_Path && r.img_Path.toLowerCase().includes(filter))
    );

    recordCountSpan.textContent = `${filtered.length} of ${allRecords.length}`;

    if (filtered.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" class="empty-cell">
            ${allRecords.length === 0 
              ? 'Catalog empty. Click <strong>Reseed Data</strong> above to initialize calibrated assets.' 
              : 'No images match your search filter.'}
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = "";

    filtered.forEach(rec => {
      const tr = document.createElement("tr");
      if (activeRecordId === rec.id) tr.classList.add("active-row");

      const formattedSize = formatBytes(rec.size);
      const pathHtml = currentOption === 2
        ? `<td class="col-path" title="${rec.img_Path}">${rec.img_Path || 'N/A'}</td>`
        : "";

      tr.innerHTML = `
        <td class="col-id">#${rec.id}</td>
        <td class="col-name">${rec.name}</td>
        <td class="col-size"><span class="badge-payload">${formattedSize}</span></td>
        <td class="col-mime">${rec.img_type}</td>
        <td class="col-action">
          <button class="btn-fetch" data-id="${rec.id}">View Img</button>
        </td>
        ${pathHtml}
      `;

      tr.addEventListener("click", () => executeBenchmark(rec));
      tableBody.appendChild(tr);
    });
  }

  // ==========================================================================
  // Core Benchmarking Latency Execution
  // ==========================================================================
  async function executeBenchmark(record) {
    activeRecordId = record.id;

    // Highlight row
    document.querySelectorAll(".benchmark-table tbody tr").forEach(r => r.classList.remove("active-row"));
    const activeRow = Array.from(document.querySelectorAll(".benchmark-table tbody tr")).find(
      r => r.querySelector(".col-id") && r.querySelector(".col-id").textContent == `#${record.id}`
    );
    if (activeRow) activeRow.classList.add("active-row");

    // UI Loading state
    rendererSubtitle.textContent = `Benchmarking fetch for ${record.name}...`;
    canvasIdleState.style.display = "none";
    canvasDisplay.style.display = "none";
    canvasLoadingState.style.display = "block";
    renderControls.style.display = "none";

    kpiBigNumber.innerHTML = `<span style="font-size: 1.6rem; color: var(--accent-amber);">Streaming...</span>`;
    kpiStatusChip.textContent = "TESTING";
    kpiStatusChip.className = "kpi-status-chip chip-bottleneck";

    const clientStart = performance.now();

    try {
      const fetchUrl = `/api/image/${record.id}?option=${currentOption}&nocache=${Date.now()}`;
      const response = await fetch(fetchUrl);

      if (!response.ok) throw new Error(`HTTP ${response.status} failed`);

      const serverLatency = parseFloat(response.headers.get("X-Response-Time-MS")) || 0;
      const storageSource = response.headers.get("X-Storage-Source") || "Unknown";
      const payloadBytes = parseInt(response.headers.get("X-Payload-Bytes")) || record.size;

      const blob = await response.blob();
      const clientEnd = performance.now();
      const totalClientMs = Math.round((clientEnd - clientStart) * 10) / 10;
      const networkClientDelta = Math.max(0.1, Math.round((totalClientMs - serverLatency) * 10) / 10);

      // Render image to canvas
      const objectUrl = URL.createObjectURL(blob);
      renderedImage.src = objectUrl;

      // Update canvas state
      canvasLoadingState.style.display = "none";
      canvasDisplay.style.display = "flex";
      renderControls.style.display = "flex";
      btnOpenFull.onclick = () => window.open(objectUrl, "_blank");

      // Update meta overlay
      metaValName.textContent = record.name;
      metaValSize.textContent = formatBytes(payloadBytes);
      metaValSource.textContent = storageSource;
      rendererSubtitle.textContent = `${record.name} rendered via ${currentOption === 1 ? 'Option 1 (DB BLOB)' : 'Option 2 (Object Storage)'}`;

      // Update Primary Response Time HUD
      kpiBigNumber.innerHTML = `${totalClientMs}<span class="kpi-unit">ms</span>`;
      
      if (currentOption === 2) {
        kpiBigNumber.style.color = "var(--accent-emerald)";
        kpiBigNumber.style.textShadow = "none";
        kpiStatusChip.textContent = "OPTIMAL";
        kpiStatusChip.className = "kpi-status-chip chip-optimal";
      } else {
        kpiBigNumber.style.color = "var(--accent-amber)";
        kpiBigNumber.style.textShadow = "none";
        kpiStatusChip.textContent = "BOTTLENECK";
        kpiStatusChip.className = "kpi-status-chip chip-bottleneck";
      }

      // Update Telemetry Breakdown Bars
      telServer.textContent = `${serverLatency} ms`;
      telClient.textContent = `${networkClientDelta} ms`;
      telPayload.textContent = formatBytes(payloadBytes);

      // Relative bar scaling
      const maxMs = Math.max(100, totalClientMs);
      telBarServer.style.width = `${Math.min(100, (serverLatency / maxMs) * 100)}%`;
      telBarClient.style.width = `${Math.min(100, (networkClientDelta / maxMs) * 100)}%`;
      telBarPayload.style.width = `${Math.min(100, (payloadBytes / (1024 * 1024)) * 100)}%`;

      // Record telemetry in history
      recordTelemetry(currentOption, totalClientMs);

    } catch (err) {
      console.error("Benchmark error:", err);
      canvasLoadingState.style.display = "none";
      canvasIdleState.style.display = "block";
      rendererSubtitle.textContent = `Fetch error: ${err.message}`;
      kpiBigNumber.innerHTML = `<span style="font-size: 1.4rem; color: var(--accent-rose);">Error</span>`;
      kpiStatusChip.textContent = "FAILED";
      kpiStatusChip.className = "kpi-status-chip chip-bottleneck";
    }
  }

  // ==========================================================================
  // Scorecard & Benchmark Calculations
  // ==========================================================================
  function recordTelemetry(option, latencyMs) {
    if (option === 1) {
      metricsHistory.option1.push(latencyMs);
    } else {
      metricsHistory.option2.push(latencyMs);
    }
    updateExecutiveScorecard();
  }

  function updateExecutiveScorecard() {
    // Scorecard removed from UI
  }

  // ==========================================================================
  // Event Listeners
  // ==========================================================================
  optionSelect.addEventListener("change", (e) => {
    currentOption = parseInt(e.target.value);
    activeRecordId = null;

    // Reset preview
    canvasDisplay.style.display = "none";
    canvasIdleState.style.display = "block";
    renderControls.style.display = "none";
    rendererSubtitle.textContent = "Click a row on the left to measure fetch latency";

    kpiBigNumber.innerHTML = `--<span class="kpi-unit">ms</span>`;
    telServer.textContent = "-- ms";
    telClient.textContent = "-- ms";
    telPayload.textContent = "-- KB";
    telBarServer.style.width = "10%";
    telBarClient.style.width = "25%";
    telBarPayload.style.width = "40%";

    updateFlowVisualizer();
    loadTableCatalog();
  });

  tableSearch.addEventListener("input", (e) => {
    currentFilter = e.target.value;
    renderTableRows();
  });

  btnRefresh.addEventListener("click", loadTableCatalog);

  // Environment chips
  chipEnvDev.addEventListener("click", () => {
    chipEnvDev.classList.add("active");
    chipEnvProd.classList.remove("active");
    pillDb.textContent = "CLOUD SQL / MYSQL";
    pillStorage.textContent = "GOOGLE CLOUD STORAGE (GCS)";
    updateFlowVisualizer();
  });

  chipEnvProd.addEventListener("click", () => {
    chipEnvProd.classList.add("active");
    chipEnvDev.classList.remove("active");
    pillDb.textContent = "AZURE SQL / MSSQL";
    pillStorage.textContent = "AZURE DATA LAKE (ADLS)";
    updateFlowVisualizer();
  });

  // Seeding
  btnSeed.addEventListener("click", async () => {
    if (!confirm("Regenerate and seed 15 calibrated benchmark assets?")) return;
    recordCountSpan.textContent = "Seeding...";
    try {
      const res = await fetch("/api/seed?count=15", { method: "POST" });
      if (res.ok) {
        alert("Seeded 15 calibrated benchmark assets successfully!");
        metricsHistory.option1 = [];
        metricsHistory.option2 = [];
        updateExecutiveScorecard();
        loadTableCatalog();
      } else {
        alert("Seeding failed.");
      }
    } catch (err) {
      alert(`Error seeding: ${err.message}`);
    }
  });

  // Architecture Blueprint Modal
  btnOpenArch.addEventListener("click", () => { modalArch.style.display = "flex"; });
  btnCloseArch.addEventListener("click", () => { modalArch.style.display = "none"; });

  // Upload Modal
  btnOpenUpload.addEventListener("click", () => { modalUpload.style.display = "flex"; });
  btnCloseUpload.addEventListener("click", () => { modalUpload.style.display = "none"; });
  btnCancelUpload.addEventListener("click", () => { modalUpload.style.display = "none"; });

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("upload-file-input");
    const targetSelect = document.getElementById("upload-target-select");
    if (!fileInput.files[0]) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("option", targetSelect.value);

    try {
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (res.ok) {
        alert(`Uploaded "${data.file}" successfully!`);
        modalUpload.style.display = "none";
        uploadForm.reset();
        loadTableCatalog();
      } else {
        alert(`Upload error: ${data.detail || "Failed"}`);
      }
    } catch (err) {
      alert(`Error uploading: ${err.message}`);
    }
  });

  // Modal Backdrop Close
  [modalArch, modalUpload].forEach(m => {
    m.addEventListener("click", (e) => {
      if (e.target === m) m.style.display = "none";
    });
  });

  function formatBytes(bytes, decimals = 1) {
    if (!+bytes) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  }

  // Boot
  loadSystemConfig();
  loadTableCatalog();
});
