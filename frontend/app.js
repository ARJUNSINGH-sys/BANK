// State Management
let activeSession = {
  accountNo: 1,
  password: "password1",
  name: "Alice",
  balance: 1000.0,
};

let transactionMode = "deposit";
let cachedCustomers = [];

// DOM Elements
const sidebar = document.querySelector("#sidebar");
const menuButton = document.querySelector("#menuButton");
const navLinks = document.querySelectorAll(".nav-link");
const modeButtons = document.querySelectorAll("[data-mode]");
const receiverField = document.querySelector("#receiverField");
const transactionForm = document.querySelector("#transactionForm");
const formResult = document.querySelector("#formResult");
const scrollButtons = document.querySelectorAll("[data-scroll]");

// Active Account & Header Elements
const sessionUserName = document.querySelector("#sessionUserName");
const sessionUserPass = document.querySelector("#sessionUserPass");
const sessionUserBalance = document.querySelector("#sessionUserBalance");
const switchAccountBtn = document.querySelector("#switchAccountBtn");
const switchAccountModal = document.querySelector("#switchAccountModal");
const closeSwitchModal = document.querySelector("#closeSwitchModal");
const sampleAccountList = document.querySelector("#sampleAccountList");
const customLoginForm = document.querySelector("#customLoginForm");

// Metrics Elements
const totalVaultBalance = document.querySelector("#totalVaultBalance");
const metricCustomerCount = document.querySelector("#metricCustomerCount");
const metricActiveAccounts = document.querySelector("#metricActiveAccounts");
const metricTransferCount = document.querySelector("#metricTransferCount");

// Form Input References
const txAccountNo = document.querySelector("#txAccountNo");
const txPassword = document.querySelector("#txPassword");
const txReceiverNo = document.querySelector("#txReceiverNo");
const txAmount = document.querySelector("#txAmount");
const txReference = document.querySelector("#txReference");

// Customer Directory & Search
const customerRows = document.querySelector("#customerRows");
const customerTableSearch = document.querySelector("#customerTableSearch");
const globalSearchInput = document.querySelector("#globalSearchInput");

// Activity Feed
const activityList = document.querySelector("#activityList");
const refreshActivityBtn = document.querySelector("#refreshActivityBtn");
const refreshBtn = document.querySelector("#refreshBtn");

// Modals
const newCustomerModal = document.querySelector("#newCustomerModal");
const openNewCustomerModalBtn = document.querySelector("#openNewCustomerModalBtn");
const addCustomerBtn = document.querySelector("#addCustomerBtn");
const closeNewCustomerModal = document.querySelector("#closeNewCustomerModal");
const newCustomerForm = document.querySelector("#newCustomerForm");

const receiptModal = document.querySelector("#receiptModal");
const closeReceiptBtn = document.querySelector("#closeReceiptBtn");

// Toast Container
const toastContainer = document.querySelector("#toastContainer");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  updateSessionUI();
  fetchAllData();
});

function setupEventListeners() {
  // Navigation & Sidebar
  menuButton?.addEventListener("click", () => sidebar?.classList.toggle("open"));
  
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.forEach((item) => item.classList.remove("active"));
      link.classList.add("active");
      sidebar?.classList.remove("open");
    });
  });

  scrollButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.querySelector(button.dataset.scroll);
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Mode Switching (Deposit / Withdraw / Transfer)
  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      transactionMode = button.dataset.mode;
      modeButtons.forEach((item) => item.classList.toggle("active", item === button));
      receiverField?.classList.toggle("is-hidden", transactionMode !== "transfer");
      showResult(`Switched mode to ${capitalize(transactionMode)}. Ready.`, "info");
    });
  });

  // Quick Amount Preset Chips
  document.querySelectorAll(".chip-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      const val = Number(chip.dataset.preset) || 0;
      const current = Number(txAmount.value) || 0;
      txAmount.value = current + val;
    });
  });

  // Transaction Form Submit
  transactionForm?.addEventListener("submit", handleTransactionSubmit);

  // Active Session Switcher Modal
  switchAccountBtn?.addEventListener("click", () => openModal(switchAccountModal));
  closeSwitchModal?.addEventListener("click", () => closeModal(switchAccountModal));
  
  customLoginForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const acc = Number(document.querySelector("#customAccNo").value);
    const pwd = document.querySelector("#customPassword").value;
    if (!acc || !pwd) return;
    setActiveSession(acc, pwd, `Account #${acc}`);
    closeModal(switchAccountModal);
  });

  // New Customer Modal
  openNewCustomerModalBtn?.addEventListener("click", () => openModal(newCustomerModal));
  addCustomerBtn?.addEventListener("click", () => openModal(newCustomerModal));
  closeNewCustomerModal?.addEventListener("click", () => closeModal(newCustomerModal));
  newCustomerForm?.addEventListener("submit", handleCreateCustomer);

  // Receipt Modal Close
  closeReceiptBtn?.addEventListener("click", () => closeModal(receiptModal));

  // Search Filters
  customerTableSearch?.addEventListener("input", filterCustomerTable);
  globalSearchInput?.addEventListener("input", (e) => {
    if (customerTableSearch) {
      customerTableSearch.value = e.target.value;
      filterCustomerTable();
    }
  });

  // Refresh Buttons
  refreshBtn?.addEventListener("click", fetchAllData);
  refreshActivityBtn?.addEventListener("click", fetchHistory);
}

// API Data Fetchers
async function fetchAllData() {
  await Promise.all([fetchMetrics(), fetchCustomers(), fetchHistory()]);
}

async function fetchMetrics() {
  try {
    const res = await fetch("/transactions/metrics");
    if (!res.ok) return;
    const data = await res.json();
    if (metricCustomerCount) metricCustomerCount.textContent = data.total_customers;
    if (metricActiveAccounts) metricActiveAccounts.textContent = data.active_accounts;
    if (metricTransferCount) metricTransferCount.textContent = data.todays_transfers;
    if (totalVaultBalance) totalVaultBalance.textContent = formatCurrency(data.total_balance);
  } catch (err) {
    console.warn("Metrics API error:", err);
  }
}

async function fetchCustomers() {
  try {
    const res = await fetch("/customers/");
    if (!res.ok) throw new Error("Failed to fetch customers");
    cachedCustomers = await res.json();
    renderCustomerTable(cachedCustomers);
    renderSampleAccounts(cachedCustomers);
    
    // Update active session balance if matches
    const active = cachedCustomers.find((c) => c.account_no === activeSession.accountNo);
    if (active) {
      activeSession.name = active.name;
      activeSession.balance = active.balance;
      updateSessionUI();
    }
  } catch (err) {
    console.error(err);
    if (customerRows) {
      customerRows.innerHTML = `
        <tr class="empty-row">
          <td colspan="7">
            <div class="table-empty">
              <strong>Unable to load customer records</strong>
              <span>Ensure backend server is running.</span>
            </div>
          </td>
        </tr>`;
    }
  }
}

async function fetchHistory() {
  try {
    const res = await fetch("/transactions/history?limit=35");
    if (!res.ok) return;
    const items = await res.json();
    renderActivityFeed(items);
  } catch (err) {
    console.warn("History API error:", err);
  }
}

// Render Functions
function renderCustomerTable(customers) {
  if (!customerRows) return;
  if (!customers || customers.length === 0) {
    customerRows.innerHTML = `
      <tr class="empty-row">
        <td colspan="7">
          <div class="table-empty">
            <strong>No customer records found</strong>
          </div>
        </td>
      </tr>`;
    return;
  }

  customerRows.innerHTML = customers
    .map(
      (c) => `
      <tr>
        <td>
          <span class="account-num-tag" title="Click to pre-fill in form" onclick="selectAccountForTx(${c.account_no})">
            #${c.account_no}
          </span>
        </td>
        <td><strong>${escapeHtml(c.name)}</strong></td>
        <td><small>${escapeHtml(c.personal_id_type)}: ${escapeHtml(c.personal_id)}</small></td>
        <td>${escapeHtml(c.branch_name || "Main Branch")}</td>
        <td>
          <div><small>Ph: ${escapeHtml(c.phone_no || "--")}</small></div>
          <div><small>Em: ${escapeHtml(c.email || "--")}</small></div>
        </td>
        <td><strong>${formatCurrency(c.balance)}</strong></td>
        <td>
          <div class="action-buttons">
            <button class="btn-action-small" onclick="quickUseAccount(${c.account_no}, '${escapeHtml(c.name)}', ${c.balance})">Use</button>
            <button class="btn-action-small danger" onclick="deleteCustomerPrompt(${c.account_no})">Delete</button>
          </div>
        </td>
      </tr>
    `
    )
    .join("");
}

function renderSampleAccounts(customers) {
  if (!sampleAccountList) return;
  sampleAccountList.innerHTML = customers
    .map(
      (c) => `
      <div class="sample-acc-item" onclick="selectSampleAccount(${c.account_no}, '${escapeHtml(c.name)}', ${c.balance})">
        <div>
          <strong>${escapeHtml(c.name)}</strong> (Acc #${c.account_no})
        </div>
        <div style="text-align:right">
          <strong style="color:var(--sbi-cyan)">${formatCurrency(c.balance)}</strong>
        </div>
      </div>
    `
    )
    .join("");
}

function renderActivityFeed(items) {
  if (!activityList) return;
  if (!items || items.length === 0) {
    activityList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">TX</div>
        <h3>No transactions recorded</h3>
        <p>Perform deposits, withdrawals, or transfers to view activity.</p>
      </div>`;
    return;
  }

  activityList.innerHTML = items
    .map((item) => {
      const typeLower = item.type.toLowerCase();
      const isPositive = typeLower === "deposit";
      return `
        <div class="activity-item">
          <div>
            <span class="activity-type-badge ${typeLower}">${item.type}</span>
            <div class="activity-info">
              <strong>Account #${item.account_no} ${item.receiver_account ? '→ Acc #' + item.receiver_account : ''}</strong>
              <span>${escapeHtml(item.reference || 'Bank transaction')} • ${formatTime(item.timestamp)}</span>
            </div>
          </div>
          <div class="activity-amount ${isPositive ? 'positive' : 'negative'}">
            ${isPositive ? '+' : '-'}${formatCurrency(item.amount)}
          </div>
        </div>
      `;
    })
    .join("");
}

// Transaction Handling
async function handleTransactionSubmit(event) {
  event.preventDefault();
  const acc = Number(txAccountNo.value);
  const pwd = txPassword.value.trim();
  const receiverAcc = Number(txReceiverNo.value);
  const amount = Number(txAmount.value);
  const refNote = txReference.value.trim() || `${capitalize(transactionMode)} Operation`;

  if (!acc || !pwd) {
    showResult("Please enter account number and password.", "error");
    showToast("Missing account credentials", "error");
    return;
  }

  if (!amount || amount <= 0) {
    showResult("Amount must be a positive number.", "error");
    showToast("Invalid amount", "error");
    return;
  }

  if (transactionMode === "transfer" && (!receiverAcc || receiverAcc === acc)) {
    showResult("Invalid receiver account number.", "error");
    showToast("Invalid transfer target", "error");
    return;
  }

  showResult(`Processing ${transactionMode}...`, "info");

  try {
    let response, data;
    if (transactionMode === "deposit") {
      response = await fetch("/transactions/deposit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_no: acc, password: pwd, amount, reference: refNote }),
      });
    } else if (transactionMode === "withdraw") {
      response = await fetch("/transactions/withdraw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_no: acc, password: pwd, amount, reference: refNote }),
      });
    } else if (transactionMode === "transfer") {
      response = await fetch("/transactions/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender_account_no: acc,
          password: pwd,
          receiver_account_no: receiverAcc,
          amount,
          reference: refNote,
        }),
      });
    }

    data = await response.json();

    if (!response.ok) {
      const msg = data.detail || "Transaction failed";
      showResult(msg, "error");
      showToast(msg, "error");
      return;
    }

    showResult(`${capitalize(transactionMode)} executed successfully!`, "success");
    showToast(`${capitalize(transactionMode)} of ${formatCurrency(amount)} successful!`, "success");

    // Open Receipt Modal
    const newBal = data.balance !== undefined ? data.balance : data.sender_balance;
    openReceiptModal({
      type: transactionMode.toUpperCase(),
      amount,
      accountNo: acc,
      receiverNo: receiverAcc,
      balance: newBal,
      reference: refNote,
      timestamp: new Date().toLocaleString(),
    });

    // Refresh Data
    await fetchAllData();
    txAmount.value = "";
    txReference.value = "";

  } catch (err) {
    console.error(err);
    showResult("Network or server connection error.", "error");
    showToast("Connection error", "error");
  }
}

// New Customer Registration
async function handleCreateCustomer(e) {
  e.preventDefault();
  const formData = new FormData(newCustomerForm);
  const payload = {
    name: formData.get("name"),
    password: formData.get("password"),
    personal_id_type: formData.get("personal_id_type"),
    personal_id: formData.get("personal_id"),
    phone_no: formData.get("phone_no"),
    email: formData.get("email"),
    address: formData.get("address"),
    branch_no: 1,
  };

  try {
    const res = await fetch("/customers/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Failed to create customer", "error");
      return;
    }

    showToast(`Customer account #${data.customer_id} created successfully!`, "success");
    closeModal(newCustomerModal);
    newCustomerForm.reset();
    await fetchAllData();

  } catch (err) {
    showToast("Failed to connect to backend", "error");
  }
}

// Delete Customer
async function deleteCustomerPrompt(accountNo) {
  const pwd = prompt(`To delete Customer Account #${accountNo}, enter session password:`, activeSession.password);
  if (!pwd) return;

  try {
    const res = await fetch(`/customers/${accountNo}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ account_no: activeSession.accountNo, password: pwd }),
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Delete failed", "error");
      return;
    }

    showToast(`Account #${accountNo} deleted successfully.`, "success");
    await fetchAllData();
  } catch (err) {
    showToast("Delete request failed", "error");
  }
}

// Session Helpers
function setActiveSession(accountNo, password, name) {
  activeSession.accountNo = accountNo;
  activeSession.password = password;
  activeSession.name = name;
  updateSessionUI();
  showToast(`Active session set to Account #${accountNo}`, "success");
}

function updateSessionUI() {
  if (sessionUserName) sessionUserName.textContent = `${activeSession.name} (#${activeSession.accountNo})`;
  if (sessionUserPass) sessionUserPass.textContent = activeSession.password;
  if (sessionUserBalance) sessionUserBalance.textContent = formatCurrency(activeSession.balance);

  // Auto pre-fill transaction form
  if (txAccountNo) txAccountNo.value = activeSession.accountNo;
  if (txPassword) txPassword.value = activeSession.password;
}

window.selectSampleAccount = function (accNo, name, balance) {
  let pwd = "password1";
  if (accNo === 2) pwd = "password2";
  if (accNo === 3) pwd = "password3";
  setActiveSession(accNo, pwd, name);
  activeSession.balance = balance;
  updateSessionUI();
  closeModal(switchAccountModal);
};

window.quickUseAccount = function (accNo, name, balance) {
  selectSampleAccount(accNo, name, balance);
};

window.selectAccountForTx = function (accNo) {
  if (transactionMode === "transfer") {
    if (txReceiverNo) txReceiverNo.value = accNo;
    showToast(`Set receiver account to #${accNo}`, "info");
  } else {
    if (txAccountNo) txAccountNo.value = accNo;
    showToast(`Set active account to #${accNo}`, "info");
  }
};

// Modals & UI Helpers
function openModal(modal) {
  modal?.classList.add("open");
}

function closeModal(modal) {
  modal?.classList.remove("open");
}

function openReceiptModal(info) {
  const receiptAmount = document.querySelector("#receiptAmount");
  const receiptType = document.querySelector("#receiptType");
  const receiptAccount = document.querySelector("#receiptAccount");
  const receiptReceiverRow = document.querySelector("#receiptReceiverRow");
  const receiptReceiver = document.querySelector("#receiptReceiver");
  const receiptBalance = document.querySelector("#receiptBalance");
  const receiptRef = document.querySelector("#receiptRef");
  const receiptTime = document.querySelector("#receiptTime");

  if (receiptAmount) receiptAmount.textContent = formatCurrency(info.amount);
  if (receiptType) receiptType.textContent = info.type;
  if (receiptAccount) receiptAccount.textContent = `Account #${info.accountNo}`;
  
  if (info.type === "TRANSFER" && receiptReceiverRow && receiptReceiver) {
    receiptReceiverRow.classList.remove("is-hidden");
    receiptReceiver.textContent = `Account #${info.receiverNo}`;
  } else if (receiptReceiverRow) {
    receiptReceiverRow.classList.add("is-hidden");
  }

  if (receiptBalance) receiptBalance.textContent = formatCurrency(info.balance);
  if (receiptRef) receiptRef.textContent = info.reference;
  if (receiptTime) receiptTime.textContent = info.timestamp;

  openModal(receiptModal);
}

function filterCustomerTable() {
  const query = (customerTableSearch?.value || "").toLowerCase().trim();
  if (!query) {
    renderCustomerTable(cachedCustomers);
    return;
  }
  const filtered = cachedCustomers.filter(
    (c) =>
      String(c.account_no).includes(query) ||
      c.name.toLowerCase().includes(query) ||
      (c.email && c.email.toLowerCase().includes(query)) ||
      (c.personal_id && c.personal_id.toLowerCase().includes(query))
  );
  renderCustomerTable(filtered);
}

function showResult(message, type) {
  if (!formResult) return;
  formResult.textContent = message;
  formResult.dataset.type = type;
}

function showToast(message, type = "info") {
  if (!toastContainer) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

function formatCurrency(amount) {
  const val = Number(amount) || 0;
  return "₹" + val.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatTime(timestampStr) {
  if (!timestampStr) return "Just now";
  return timestampStr.replace("T", " ").split(".")[0];
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
