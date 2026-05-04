-- ============================================================
--  Personal Expense Tracker - MySQL Setup
--  Run this file once to initialize the database
-- ============================================================

-- 1. Create & select the database
CREATE DATABASE IF NOT EXISTS expense_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE expense_tracker;

-- 2. Categories table
CREATE TABLE IF NOT EXISTS categories (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  icon VARCHAR(10)  NOT NULL DEFAULT '💰',
  color VARCHAR(7)  NOT NULL DEFAULT '#6366f1'
);

-- 3. Expenses table
CREATE TABLE IF NOT EXISTS expenses (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  amount      DECIMAL(10,2) NOT NULL,
  category_id INT           NOT NULL,
  date        DATE          NOT NULL,
  description TEXT,
  created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- 4. Seed categories
INSERT IGNORE INTO categories (name, icon, color) VALUES
  ('Food',          '🍔', '#f97316'),
  ('Travel',        '✈️',  '#06b6d4'),
  ('Shopping',      '🛍️',  '#ec4899'),
  ('Medicines',     '💊', '#10b981'),
  ('Bills',         '🧾', '#8b5cf6'),
  ('Entertainment', '🎬', '#f59e0b'),
  ('Education',     '📚', '#3b82f6'),
  ('Others',        '📦', '#6b7280');

-- 5. Sample expense data (last 3 months)
INSERT INTO expenses (amount, category_id, date, description) VALUES
  (250.00,  1, CURDATE() - INTERVAL 2  DAY, 'Groceries from supermarket'),
  (1200.00, 2, CURDATE() - INTERVAL 5  DAY, 'Train tickets to Pune'),
  (3500.00, 3, CURDATE() - INTERVAL 7  DAY, 'New clothes shopping'),
  (180.00,  4, CURDATE() - INTERVAL 3  DAY, 'Monthly medicines'),
  (2100.00, 5, CURDATE() - INTERVAL 1  DAY, 'Electricity bill'),
  (600.00,  6, CURDATE() - INTERVAL 10 DAY, 'Movie and dinner outing'),
  (4500.00, 7, CURDATE() - INTERVAL 12 DAY, 'Online course subscription'),
  (150.00,  1, CURDATE() - INTERVAL 15 DAY, 'Restaurant lunch'),
  (800.00,  2, CURDATE() - INTERVAL 20 DAY, 'Cab rides this week'),
  (1500.00, 3, CURDATE() - INTERVAL 25 DAY, 'Electronics accessories'),
  (300.00,  4, CURDATE() - INTERVAL 8  DAY, 'Doctor consultation'),
  (900.00,  5, CURDATE() - INTERVAL 2  DAY, 'Internet bill'),
  (450.00,  6, CURDATE() - INTERVAL 18 DAY, 'Streaming services'),
  (200.00,  8, CURDATE() - INTERVAL 22 DAY, 'Miscellaneous expenses'),
  -- last month
  (320.00,  1, CURDATE() - INTERVAL 35 DAY, 'Weekly groceries'),
  (2800.00, 5, CURDATE() - INTERVAL 40 DAY, 'Rent partial payment'),
  (750.00,  2, CURDATE() - INTERVAL 45 DAY, 'Uber rides'),
  (5000.00, 7, CURDATE() - INTERVAL 50 DAY, 'Books purchase'),
  (1100.00, 3, CURDATE() - INTERVAL 38 DAY, 'Online shopping'),
  (280.00,  4, CURDATE() - INTERVAL 42 DAY, 'Pharmacy'),
  -- two months ago
  (400.00,  1, CURDATE() - INTERVAL 65 DAY, 'Groceries'),
  (3200.00, 5, CURDATE() - INTERVAL 62 DAY, 'Monthly bills'),
  (900.00,  6, CURDATE() - INTERVAL 70 DAY, 'Weekend entertainment'),
  (600.00,  2, CURDATE() - INTERVAL 75 DAY, 'Travel expenses'),
  (1800.00, 3, CURDATE() - INTERVAL 68 DAY, 'Clothing');
