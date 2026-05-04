# 💰 SpendWise – Personal Expense Tracker

A full-stack expense tracking web application built with **Flask**, **MySQL**, and **Vanilla JS**.

---

## 📁 Project Structure

```
expense_tracker/
├── app.py                 ← Flask backend (REST API + page routes)
├── requirements.txt       ← Python dependencies
├── setup.sql              ← MySQL schema + seed data
├── templates/
│   ├── base.html          ← Shared layout (sidebar, modal, toast)
│   ├── index.html         ← Overview page
│   ├── dashboard.html     ← Charts & analytics
│   └── history.html       ← Full transaction history + filters
└── static/
    ├── style.css          ← All styles (dark theme, animations)
    └── app.js             ← Shared JS utilities & modal logic
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.9+
- MySQL 8.0+ (running locally or remote)
- pip

---

### 2. MySQL Database Setup

Open your MySQL client and run:

```sql
SOURCE /path/to/expense_tracker/setup.sql;
```

Or copy-paste the contents of `setup.sql` into MySQL Workbench / phpMyAdmin.

This will:
- Create the `expense_tracker` database
- Create `categories` and `expenses` tables
- Insert 8 default categories and 25 sample expenses

---

### 3. Configure Database Connection

Edit **`app.py`** (lines ~22-29) with your MySQL credentials:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "YOUR_PASSWORD_HERE",   # ← change this
    "database": "expense_tracker",
    ...
}
```

Or set environment variables before running:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASS=yourpassword
export DB_NAME=expense_tracker
```

---

### 4. Install Python Dependencies

```bash
cd expense_tracker
pip install -r requirements.txt
```

---

### 5. Run the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🌐 Pages

| URL          | Description                              |
|--------------|------------------------------------------|
| `/`          | Overview – KPI cards, recent transactions, mini donut chart |
| `/dashboard` | Charts – monthly trend bar + category doughnut, category breakdown cards |
| `/history`   | Full history – filterable table, search, CSV export |

---

## 🔌 REST API Endpoints

| Method | Endpoint                    | Description               |
|--------|-----------------------------|---------------------------|
| GET    | `/api/categories`           | List all categories       |
| GET    | `/api/expenses`             | List expenses (filterable)|
| POST   | `/api/expenses`             | Add new expense           |
| PUT    | `/api/expenses/<id>`        | Update expense            |
| DELETE | `/api/expenses/<id>`        | Delete expense            |
| GET    | `/api/summary/dashboard`    | Dashboard aggregates      |
| GET    | `/api/summary/monthly`      | Monthly totals (trend)    |
| GET    | `/api/summary/categories`   | Category totals           |
| GET    | `/api/export/csv`           | Download CSV              |

### Query Parameters for `/api/expenses`

| Param      | Example        | Description            |
|------------|----------------|------------------------|
| `month`    | `2025-04`      | Filter by month        |
| `category` | `3`            | Filter by category ID  |
| `search`   | `groceries`    | Search in description  |
| `limit`    | `50`           | Max results (def. 200) |

---

## ✨ Features

- **Add / Edit / Delete** expenses via animated modal
- **Category badges** with colour coding
- **Monthly trend** bar chart (last 6 months)
- **Category doughnut** chart per month
- **KPI cards** – total, daily average, top category
- **Filter** by month, category, text search
- **Export CSV** (respects current filters)
- **Responsive** – works on mobile & desktop
- **Dark editorial** theme with smooth animations

---

## ➕ Adding More Categories

Run SQL directly:

```sql
USE expense_tracker;
INSERT INTO categories (name, icon, color)
VALUES ('Gym', '🏋️', '#14b8a6');
```

Or extend the seed in `setup.sql` before running it.

---

## 🛠 Troubleshooting

| Issue | Fix |
|-------|-----|
| `Access denied for user` | Check DB_USER / DB_PASS in app.py |
| `Unknown database` | Run setup.sql first |
| `ModuleNotFoundError: pymysql` | `pip install pymysql` |
| Charts not showing | Check browser console; CDN requires internet |
| CSS not loading | Make sure `static/style.css` exists |
