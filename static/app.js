async function api(url, options = {}) {
  try {
    const res  = await fetch(url, options);
    const json = await res.json();
    if (!json.success) throw new Error(json.error || "API error");
    return json;
  } catch (err) {
    console.error("API Error [" + url + "]:", err.message);
    throw err;
  }
}

function formatCurrency(n) {
  return "₹" + Number(n).toLocaleString("en-IN", {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
}

function currentYearMonth() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
}

function formatMonthLabel(ym) {
  if (!ym) return "—";
  const [y, m] = ym.split("-");
  return new Date(y, m - 1).toLocaleDateString("en-IN", { month: "long", year: "numeric" });
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso + "T00:00:00").toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric"
  });
}

function transactionRow(e) {
  return `
    <div class="tx-row">
      <div class="tx-icon" style="background:${e.category_color}22">
        ${e.category_icon}
      </div>
      <div class="tx-meta">
        <p class="tx-name">${e.category_name}${e.description ? " – " + e.description : ""}</p>
        <p class="tx-date">${formatDate(e.date)}</p>
      </div>
      <span class="tx-amount">${formatCurrency(e.amount)}</span>
    </div>`;
}

/* ── Toast ──────────────────────────────────────────────────── */
let toastTimer;
function showToast(msg, type = "success") {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.className   = "toast " + type + " show";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = "toast"; }, 3200);
}

/* ── Mobile sidebar toggle ──────────────────────────────────── */
const hamburgerBtn = document.getElementById("hamburgerBtn");
const sidebar      = document.getElementById("sidebar");

if (hamburgerBtn && sidebar) {
  hamburgerBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
  document.addEventListener("click", e => {
    if (sidebar.classList.contains("open") &&
        !sidebar.contains(e.target) &&
        e.target !== hamburgerBtn) {
      sidebar.classList.remove("open");
    }
  });
}

/* ── Category cache ─────────────────────────────────────────── */
let _categoriesCache = null;

async function getCategories() {
  if (_categoriesCache) return _categoriesCache;
  const res = await api("/api/categories");
  _categoriesCache = res.data;
  return _categoriesCache;
}

/* ── Populate any <select> with categories ──────────────────── */
async function populateCategorySelect(selectEl, includeAll = false) {
  if (!selectEl) return;

  selectEl.innerHTML = includeAll
    ? '<option value="">All categories</option>'
    : '<option value="">Select category…</option>';

  try {
    const cats = await getCategories();
    if (!cats || cats.length === 0) {
      console.warn("No categories returned from API");
      return;
    }
    cats.forEach(c => {
      const opt = document.createElement("option");
      opt.value       = c.id;
      opt.textContent = c.icon + " " + c.name;
      selectEl.appendChild(opt);
    });
    console.log("Categories loaded into select:", cats.length);
  } catch (err) {
    console.error("Failed to load categories:", err.message);
    showToast("Could not load categories. Is Flask running on port 5000?", "error");
  }
}

/* ── Expense Modal ──────────────────────────────────────────── */
const overlay     = document.getElementById("modalOverlay");
const modalTitle  = document.getElementById("modalTitle");
const expenseForm = document.getElementById("expenseForm");
const expenseId   = document.getElementById("expenseId");
const expAmount   = document.getElementById("expAmount");
const expDate     = document.getElementById("expDate");
const expCategory = document.getElementById("expCategory");
const expDesc     = document.getElementById("expDesc");

// Load categories into modal dropdown as soon as script runs
if (expCategory) {
  populateCategorySelect(expCategory, false);
}

function openModal(title) {
  if (modalTitle) modalTitle.textContent = title || "Add Expense";
  if (overlay)    overlay.classList.add("active");

  // Safety net: reload categories if dropdown is empty
  if (expCategory && expCategory.options.length <= 1) {
    populateCategorySelect(expCategory, false);
  }

  setTimeout(() => { if (expAmount) expAmount.focus(); }, 100);
}

function closeModal() {
  if (overlay)     overlay.classList.remove("active");
  if (expenseForm) expenseForm.reset();
  if (expenseId)   expenseId.value = "";
}

// "Add Expense" button global setup
const addBtn = document.getElementById("openAddModal");
if (addBtn) {
  addBtn.addEventListener("click", () => {
    if (expDate) expDate.value = new Date().toISOString().split("T")[0];
    openModal("Add Expense");
  });
}

// Global hook to make triggering openModal from other templates easy
window.openAddModal = function() {
  if (expDate) expDate.value = new Date().toISOString().split("T")[0];
  openModal("Add Expense");
};

// Close modal triggers
const modalClose = document.getElementById("modalClose");
const cancelBtn  = document.getElementById("cancelBtn");
if (modalClose) modalClose.addEventListener("click", closeModal);
if (cancelBtn)  cancelBtn.addEventListener("click",  closeModal);
if (overlay)    overlay.addEventListener("click", e => { if (e.target === overlay) closeModal(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

/* ── Submit form ────────────────────────────────────────────── */
if (expenseForm) {
  expenseForm.addEventListener("submit", async e => {
    e.preventDefault();

    const id = expenseId ? expenseId.value.trim() : "";

    // Inline validation
    if (!expAmount || !expAmount.value || parseFloat(expAmount.value) <= 0) {
      showToast("Please enter a valid amount", "error"); return;
    }
    if (!expCategory || !expCategory.value) {
      showToast("Please select a category", "error"); return;
    }
    if (!expDate || !expDate.value) {
      showToast("Please select a date", "error"); return;
    }

    const body = {
      amount:      parseFloat(expAmount.value),
      category_id: parseInt(expCategory.value),
      date:        expDate.value,
      description: expDesc ? expDesc.value.trim() : "",
    };

    const submitBtn = document.getElementById("submitBtn");
    if (submitBtn) {
      submitBtn.disabled    = true;
      submitBtn.textContent = "Saving…";
    }

    try {
      if (id) {
        await api("/api/expenses/" + id, {
          method:  "PUT",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(body),
        });
        showToast("Expense updated ✓");
      } else {
        await api("/api/expenses", {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(body),
        });
        showToast("Expense added ✓");
      }
      closeModal();

      // Refresh data on the active page contextually
      if (typeof window.loadExpenses === "function") window.loadExpenses();
      if (typeof window.loadDashboard === "function") {
        const dp = document.getElementById("dashMonth");
        window.loadDashboard(dp ? dp.value : currentYearMonth());
      }

    } catch (err) {
      showToast("Error: " + err.message, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled    = false;
        submitBtn.textContent = "Save Expense";
      }
    }
  });
}

/* ── Edit modal ─────────────────────────────────────────────── */
async function openEditModal(id) {
  try {
    // Ensure categories are loaded first
    await populateCategorySelect(expCategory, false);

    const res = await api("/api/expenses?limit=2000");
    const exp = res.data.find(e => String(e.id) === String(id));
    if (!exp) { showToast("Expense not found", "error"); return; }

    if (expenseId) expenseId.value = exp.id;
    if (expAmount) expAmount.value = parseFloat(exp.amount);
    if (expDate)   expDate.value   = exp.date;
    if (expDesc)   expDesc.value   = exp.description || "";

    // Set category value safely after the DOM clears its rendering task
    setTimeout(() => {
      if (expCategory) expCategory.value = String(exp.category_id);
    }, 30);

    openModal("Edit Expense");
  } catch (err) {
    showToast("Could not load expense: " + err.message, "error");
  }
}

/* ── Delete confirm dialog ──────────────────────────────────── */
function confirmDelete(id) {
  const dlg = document.createElement("div");
  dlg.className = "confirm-overlay";
  dlg.innerHTML = `
    <div class="confirm-box">
      <h3>Delete expense?</h3>
      <p>This action cannot be undone.</p>
      <div class="confirm-actions">
        <button class="btn btn-ghost" id="cancelDel">Cancel</button>
        <button class="btn btn-danger" id="confirmDel">Delete</button>
      </div>
    </div>`;
  document.body.appendChild(dlg);

  dlg.querySelector("#cancelDel").addEventListener("click",  () => dlg.remove());
  dlg.querySelector("#confirmDel").addEventListener("click", async () => {
    try {
      await api("/api/expenses/" + id, { method: "DELETE" });
      showToast("Expense deleted");
      dlg.remove();
      if (typeof window.loadExpenses === "function") window.loadExpenses();
    } catch (err) {
      showToast("Delete failed: " + err.message, "error");
      dlg.remove();
    }
  });

  dlg.addEventListener("click", e => { if (e.target === dlg) dlg.remove(); });
}

// Bind crucial callbacks explicitly to window for templates rendering content dynamically
window.api = api;
window.formatCurrency = formatCurrency;
window.currentYearMonth = currentYearMonth;
window.formatMonthLabel = formatMonthLabel;
window.formatDate = formatDate;
window.transactionRow = transactionRow;
window.showToast = showToast;
window.populateCategorySelect = populateCategorySelect;
window.openModal = openModal;
window.closeModal = closeModal;
window.openEditModal = openEditModal;
window.confirmDelete = confirmDelete;