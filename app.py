"""
Personal Expense Tracker - Flask Backend
=========================================
Run:  python app.py
API base: http://localhost:5000/api
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
import pymysql
import pymysql.cursors
from datetime import datetime, date
import csv
import io
import os

app = Flask(__name__)

# ─────────────────────────────────────────
#  Database configuration  ← edit here
# ─────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",   "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER",   "root"),
    "password": os.getenv("DB_PASS",   "root123"),  
    "database": os.getenv("DB_NAME",   "expense_tracker"),
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_db():
    """Return a fresh pymysql connection."""
    return pymysql.connect(**DB_CONFIG)


# ─────────────────────────────────────────
#  Page routes
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/history")
def history():
    return render_template("history.html")


# ─────────────────────────────────────────
#  API: Categories
# ─────────────────────────────────────────

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Return all expense categories."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM categories ORDER BY name")
            categories = cur.fetchall()
        conn.close()
        return jsonify({"success": True, "data": categories})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
#  API: Expenses – CRUD
# ─────────────────────────────────────────

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    """
    Query params:
      month      – YYYY-MM  (optional)
      category   – category id (optional)
      search     – text search in description (optional)
      limit      – default 200
    """
    month    = request.args.get("month")       # e.g. "2025-04"
    category = request.args.get("category")    # e.g. "3"
    search   = request.args.get("search", "").strip()
    limit    = int(request.args.get("limit", 200))

    sql = """
        SELECT e.id, e.amount, e.date, e.description, e.created_at,
               c.id   AS category_id,
               c.name AS category_name,
               c.icon AS category_icon,
               c.color AS category_color
        FROM   expenses e
        JOIN   categories c ON c.id = e.category_id
        WHERE  1=1
    """
    params = []

    if month:
        sql += " AND DATE_FORMAT(e.date, '%%Y-%%m') = %s"
        params.append(month)

    if category:
        sql += " AND e.category_id = %s"
        params.append(category)

    if search:
        sql += " AND e.description LIKE %s"
        params.append(f"%{search}%")

    sql += " ORDER BY e.date DESC, e.id DESC LIMIT %s"
    params.append(limit)

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        conn.close()

        # Convert date objects to strings for JSON serialisation
        for r in rows:
            if isinstance(r["date"], date):
                r["date"] = r["date"].isoformat()
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].isoformat()

        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    """Add a new expense. Expects JSON body."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    amount      = data.get("amount")
    category_id = data.get("category_id")
    exp_date    = data.get("date")
    description = data.get("description", "").strip()

    # Basic validation
    if not amount or not category_id or not exp_date:
        return jsonify({"success": False,
                        "error": "amount, category_id and date are required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO expenses (amount, category_id, date, description)
                   VALUES (%s, %s, %s, %s)""",
                (amount, category_id, exp_date, description or None)
            )
            new_id = cur.lastrowid
        conn.close()
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    """Update an existing expense."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    amount      = data.get("amount")
    category_id = data.get("category_id")
    exp_date    = data.get("date")
    description = data.get("description", "").strip()

    if not amount or not category_id or not exp_date:
        return jsonify({"success": False,
                        "error": "amount, category_id and date are required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE expenses
                   SET    amount=%s, category_id=%s, date=%s, description=%s
                   WHERE  id=%s""",
                (amount, category_id, exp_date, description or None, expense_id)
            )
            affected = cur.rowcount
        conn.close()
        if affected == 0:
            return jsonify({"success": False, "error": "Expense not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    """Delete an expense by id."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
            affected = cur.rowcount
        conn.close()
        if affected == 0:
            return jsonify({"success": False, "error": "Expense not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
#  API: Analytics / Summary
# ─────────────────────────────────────────

@app.route("/api/summary/monthly", methods=["GET"])
def monthly_summary():
    """
    Returns per-month totals for the last N months.
    Query param: months (default 6)
    """
    months = int(request.args.get("months", 6))
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT DATE_FORMAT(date, '%%Y-%%m') AS month,
                          SUM(amount)                 AS total,
                          COUNT(*)                    AS count
                   FROM   expenses
                   WHERE  date >= CURDATE() - INTERVAL %s MONTH
                   GROUP  BY month
                   ORDER  BY month DESC""",
                (months,)
            )
            rows = cur.fetchall()
        conn.close()
        for r in rows:
            r["total"] = float(r["total"])
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/summary/categories", methods=["GET"])
def category_summary():
    """
    Category-wise totals.
    Query param: month (YYYY-MM, optional – defaults to current month)
    """
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT c.id, c.name, c.icon, c.color,
                          COALESCE(SUM(e.amount), 0) AS total,
                          COUNT(e.id)                AS count
                   FROM   categories c
                   LEFT JOIN expenses e
                          ON e.category_id = c.id
                         AND DATE_FORMAT(e.date, '%%Y-%%m') = %s
                   GROUP  BY c.id
                   ORDER  BY total DESC""",
                (month,)
            )
            rows = cur.fetchall()
        conn.close()
        for r in rows:
            r["total"] = float(r["total"])
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/summary/dashboard", methods=["GET"])
def dashboard_summary():
    """Aggregate data for the main dashboard."""
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Current month total
            cur.execute(
                """SELECT COALESCE(SUM(amount), 0) AS total,
                          COUNT(*) AS count
                   FROM   expenses
                   WHERE  DATE_FORMAT(date, '%%Y-%%m') = %s""",
                (month,)
            )
            month_row = cur.fetchone()

            # Category breakdown for month
            cur.execute(
                """SELECT c.name, c.icon, c.color,
                          COALESCE(SUM(e.amount), 0) AS total
                   FROM   categories c
                   LEFT JOIN expenses e
                          ON e.category_id = c.id
                         AND DATE_FORMAT(e.date, '%%Y-%%m') = %s
                   GROUP  BY c.id
                   ORDER  BY total DESC""",
                (month,)
            )
            categories = cur.fetchall()

            # Monthly trend (last 6 months)
            cur.execute(
                """SELECT DATE_FORMAT(date, '%%Y-%%m') AS month,
                          SUM(amount) AS total
                   FROM   expenses
                   WHERE  date >= CURDATE() - INTERVAL 6 MONTH
                   GROUP  BY month
                   ORDER  BY month ASC"""
            )
            trend = cur.fetchall()

            # Latest 5 transactions
            cur.execute(
                """SELECT e.id, e.amount, e.date, e.description,
                          c.name AS category_name, c.icon AS category_icon, c.color AS category_color
                   FROM   expenses e
                   JOIN   categories c ON c.id = e.category_id
                   ORDER  BY e.date DESC, e.id DESC
                   LIMIT  5"""
            )
            recent = cur.fetchall()

        conn.close()

        for r in categories:
            r["total"] = float(r["total"])
        for r in trend:
            r["total"] = float(r["total"])
        for r in recent:
            if isinstance(r["date"], date):
                r["date"] = r["date"].isoformat()

        return jsonify({
            "success": True,
            "data": {
                "month_total":  float(month_row["total"]),
                "month_count":  month_row["count"],
                "categories":   categories,
                "trend":        trend,
                "recent":       recent,
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
#  Export: CSV
# ─────────────────────────────────────────

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Export expenses as a CSV download."""
    month    = request.args.get("month")
    category = request.args.get("category")

    sql = """
        SELECT e.id, e.date, c.name AS category, e.amount, e.description
        FROM   expenses e
        JOIN   categories c ON c.id = e.category_id
        WHERE  1=1
    """
    params = []

    if month:
        sql += " AND DATE_FORMAT(e.date, '%%Y-%%m') = %s"
        params.append(month)
    if category:
        sql += " AND e.category_id = %s"
        params.append(category)

    sql += " ORDER BY e.date DESC"

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.DictWriter(output,
                                fieldnames=["id", "date", "category", "amount", "description"])
        writer.writeheader()
        for r in rows:
            if isinstance(r["date"], date):
                r["date"] = r["date"].isoformat()
            writer.writerow(r)

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=expenses.csv"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
