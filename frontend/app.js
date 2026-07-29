const initialCustomers = [
  {
    id: 1,
    password: "password1",
    name: "Alice",
    personalIdType: "NID",
    personalId: "A123",
    address: "123 Cherry Ln",
    phone: "1111111111",
    email: "alice@example.com",
    branch: "Main Branch",
    balance: 1000,
  },
  {
    id: 2,
    password: "password2",
    name: "Bob",
    personalIdType: "NID",
    personalId: "B234",
    address: "456 Oak Ave",
    phone: "2222222222",
    email: "bob@example.com",
    branch: "Main Branch",
    balance: 1000,
  },
  {
    id: 3,
    password: "password3",
    name: "Charlie",
    personalIdType: "NID",
    personalId: "C345",
    address: "789 Pine Rd",
    phone: "3333333333",
    email: "charlie@example.com",
    branch: "Main Branch",
    balance: 1000,
  },
];

const storageKey = "bank-management-demo-state";

const state = loadState();
let activeAccountId = null;
let transactionMode = "deposit";

const elements = {
  sessionStatus: document.querySelector("#sessionStatus"),
  activeAccountName: document.querySelector("#activeAccountName"),
  activeAccountMeta: document.querySelector("#activeAccountMeta"),
  balanceValue: document.querySelector("#balanceValue"),
  loginForm: document.querySelector("#loginForm"),
  accountNumber: document.querySelector("#accountNumber"),
  password: document.querySelector("#password"),
  loginFeedback: document.querySelector("#loginFeedback"),
  logoutButton: document.querySelector("#logoutButton"),
  transactionForm: document.querySelector("#transactionForm"),
  transactionFeedback: document.querySelector("#transactionFeedback"),
  amount: document.querySelector("#amount"),
  receiverField: document.querySelector("#receiverField"),
  receiverAccount: document.querySelector("#receiverAccount"),
  timeline: document.querySelector("#timeline"),
  customerList: document.querySelector("#customerList"),
  resetDemo: document.querySelector("#resetDemo"),
  modeButtons: document.querySelectorAll("[data-mode]"),
  sampleButtons: document.querySelectorAll(".sample-account"),
};

elements.loginForm.addEventListener("submit", handleLogin);
elements.logoutButton.addEventListener("click", handleLogout);
elements.transactionForm.addEventListener("submit", handleTransaction);
elements.resetDemo.addEventListener("click", resetDemoData);

elements.modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

elements.sampleButtons.forEach((button) => {
  button.addEventListener("click", () => fillSampleAccount(Number(button.dataset.account)));
});

render();

function loadState() {
  const stored = localStorage.getItem(storageKey);
  if (!stored) {
    return {
      customers: structuredClone(initialCustomers),
      transactions: [],
    };
  }

  try {
    return JSON.parse(stored);
  } catch {
    return {
      customers: structuredClone(initialCustomers),
      transactions: [],
    };
  }
}

function saveState() {
  localStorage.setItem(storageKey, JSON.stringify(state));
}

function handleLogin(event) {
  event.preventDefault();
  const accountId = Number(elements.accountNumber.value);
  const password = elements.password.value;
  const customer = state.customers.find((item) => item.id === accountId && item.password === password);

  if (!customer) {
    showFeedback(elements.loginFeedback, "Login failed: incorrect account number or password.", "error");
    activeAccountId = null;
    render();
    return;
  }

  activeAccountId = customer.id;
  showFeedback(elements.loginFeedback, `Signed in as ${customer.name}.`, "success");
  render();
}

function handleLogout() {
  activeAccountId = null;
  elements.password.value = "";
  showFeedback(elements.loginFeedback, "Signed out.", "success");
  render();
}

function handleTransaction(event) {
  event.preventDefault();
  const activeCustomer = getActiveCustomer();

  if (!activeCustomer) {
    showFeedback(elements.transactionFeedback, "You must sign in before performing transactions.", "error");
    return;
  }

  const amount = Number(elements.amount.value);
  if (!Number.isFinite(amount) || amount <= 0) {
    showFeedback(elements.transactionFeedback, "Amount must be a positive number.", "error");
    return;
  }

  if (transactionMode === "withdraw" && activeCustomer.balance < amount) {
    showFeedback(elements.transactionFeedback, "Insufficient balance.", "error");
    return;
  }

  if (transactionMode === "transfer") {
    const receiver = state.customers.find((item) => item.id === Number(elements.receiverAccount.value));
    if (!receiver || receiver.id === activeCustomer.id) {
      showFeedback(elements.transactionFeedback, "Choose a valid receiver account.", "error");
      return;
    }

    if (activeCustomer.balance < amount) {
      showFeedback(elements.transactionFeedback, "Insufficient balance for transfer.", "error");
      return;
    }

    activeCustomer.balance -= amount;
    receiver.balance += amount;
    recordTransaction("transfer", amount, activeCustomer, receiver);
    showFeedback(elements.transactionFeedback, `Transferred ${formatMoney(amount)} to ${receiver.name}.`, "success");
  }

  if (transactionMode === "deposit") {
    activeCustomer.balance += amount;
    recordTransaction("deposit", amount, activeCustomer);
    showFeedback(elements.transactionFeedback, `Deposited ${formatMoney(amount)}.`, "success");
  }

  if (transactionMode === "withdraw") {
    activeCustomer.balance -= amount;
    recordTransaction("withdraw", amount, activeCustomer);
    showFeedback(elements.transactionFeedback, `Withdrew ${formatMoney(amount)}.`, "success");
  }

  elements.amount.value = "";
  saveState();
  render();
}

function setMode(mode) {
  transactionMode = mode;
  elements.modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  elements.receiverField.classList.toggle("hidden", mode !== "transfer");
  showFeedback(elements.transactionFeedback, "", "");
}

function fillSampleAccount(accountId) {
  const customer = state.customers.find((item) => item.id === accountId);
  if (!customer) return;
  elements.accountNumber.value = customer.id;
  elements.password.value = customer.password;
  showFeedback(elements.loginFeedback, `${customer.name}'s credentials filled.`, "success");
}

function resetDemoData() {
  state.customers = structuredClone(initialCustomers);
  state.transactions = [];
  activeAccountId = null;
  saveState();
  showFeedback(elements.loginFeedback, "Demo data reset.", "success");
  showFeedback(elements.transactionFeedback, "", "");
  render();
}

function recordTransaction(type, amount, actor, receiver = null) {
  state.transactions.unshift({
    id: crypto.randomUUID(),
    type,
    amount,
    actorId: actor.id,
    actorName: actor.name,
    receiverId: receiver?.id ?? null,
    receiverName: receiver?.name ?? null,
    createdAt: new Date().toISOString(),
  });
}

function render() {
  const activeCustomer = getActiveCustomer();

  elements.sessionStatus.textContent = activeCustomer ? `Active: ${activeCustomer.name}` : "No active session";
  elements.activeAccountName.textContent = activeCustomer ? activeCustomer.name : "Sign in to manage funds";
  elements.activeAccountMeta.textContent = activeCustomer
    ? `Account ${activeCustomer.id} · ${activeCustomer.branch} · ${activeCustomer.email}`
    : "Use one of the seeded customers from the Python backend.";
  elements.balanceValue.textContent = formatMoney(activeCustomer?.balance ?? 0);

  renderReceiverOptions();
  renderTimeline();
  renderCustomers();
}

function renderReceiverOptions() {
  const activeCustomer = getActiveCustomer();
  const options = state.customers
    .filter((customer) => customer.id !== activeCustomer?.id)
    .map((customer) => `<option value="${customer.id}">${customer.name} · Account ${customer.id}</option>`)
    .join("");

  elements.receiverAccount.innerHTML = options || "<option>No receiver available</option>";
}

function renderTimeline() {
  if (!state.transactions.length) {
    elements.timeline.innerHTML = `<div class="timeline-item"><span class="muted">No transactions yet.</span></div>`;
    return;
  }

  elements.timeline.innerHTML = state.transactions
    .slice(0, 8)
    .map((transaction) => {
      const sign = transaction.type === "deposit" ? "+" : "-";
      const amountClass = transaction.type === "deposit" ? "amount-positive" : transaction.type === "withdraw" ? "amount-negative" : "amount-neutral";
      const title = getTransactionTitle(transaction);

      return `
        <div class="timeline-item">
          <strong>
            <span>${title}</span>
            <span class="${amountClass}">${sign}${formatMoney(transaction.amount)}</span>
          </strong>
          <span class="muted">${formatDate(transaction.createdAt)}</span>
        </div>
      `;
    })
    .join("");
}

function renderCustomers() {
  elements.customerList.innerHTML = state.customers
    .map(
      (customer) => `
        <div class="customer-item">
          <strong>
            <span>${customer.name}</span>
            <span>${formatMoney(customer.balance)}</span>
          </strong>
          <span class="muted">Account ${customer.id} · ${customer.email}</span>
          <span class="muted">${customer.address}</span>
        </div>
      `,
    )
    .join("");
}

function getTransactionTitle(transaction) {
  if (transaction.type === "transfer") {
    return `${transaction.actorName} to ${transaction.receiverName}`;
  }
  return `${capitalize(transaction.type)} by ${transaction.actorName}`;
}

function getActiveCustomer() {
  return state.customers.find((customer) => customer.id === activeAccountId) ?? null;
}

function showFeedback(element, message, type) {
  element.textContent = message;
  element.className = `feedback ${type}`.trim();
}

function formatMoney(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
