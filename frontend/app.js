const sidebar = document.querySelector("#sidebar");
const menuButton = document.querySelector("#menuButton");
const navLinks = document.querySelectorAll(".nav-link");
const modeButtons = document.querySelectorAll("[data-mode]");
const receiverField = document.querySelector("#receiverField");
const transactionForm = document.querySelector("#transactionForm");
const formResult = document.querySelector("#formResult");
const scrollButtons = document.querySelectorAll("[data-scroll]");

let transactionMode = "deposit";

menuButton?.addEventListener("click", () => {
  sidebar?.classList.toggle("open");
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.forEach((item) => item.classList.remove("active"));
    link.classList.add("active");
    sidebar?.classList.remove("open");
  });
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    transactionMode = button.dataset.mode;
    modeButtons.forEach((item) => item.classList.toggle("active", item === button));
    receiverField?.classList.toggle("is-hidden", transactionMode !== "transfer");
    showResult("Transaction form ready.", "info");
  });
});

scrollButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.querySelector(button.dataset.scroll);
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

transactionForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(transactionForm);
  const accountNumber = String(formData.get("accountNumber") || "").trim();
  const receiverAccount = String(formData.get("receiverAccount") || "").trim();
  const amount = Number(formData.get("amount"));

  if (!accountNumber) {
    showResult("Enter an account number before preparing the transaction.", "error");
    return;
  }

  if (!Number.isFinite(amount) || amount <= 0) {
    showResult("Enter a valid positive amount.", "error");
    return;
  }

  if (transactionMode === "transfer" && !receiverAccount) {
    showResult("Enter a receiver account for transfer transactions.", "error");
    return;
  }

  showResult(
    `${capitalize(transactionMode)} request is ready for your Supabase mutation logic.`,
    "success",
  );
});

document.addEventListener("click", (event) => {
  const clickedInsideSidebar = sidebar?.contains(event.target);
  const clickedMenu = menuButton?.contains(event.target);

  if (!clickedInsideSidebar && !clickedMenu) {
    sidebar?.classList.remove("open");
  }
});

function showResult(message, type) {
  if (!formResult) return;
  formResult.textContent = message;
  formResult.dataset.type = type;
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
