-- Foreign Key Constraints enforcement in SQLite
PRAGMA foreign_keys = ON;


-- ============================================================================
-- DATABASE VIEWS
-- ============================================================================

-- VComplete Inventory Master Summary
-- Encapsulates multi-table joins into a reusable virtual table
DROP VIEW IF EXISTS v_inventory_summary;
CREATE VIEW IF NOT EXISTS v_inventory_summary AS
SELECT
    p.product_id,
    p.sku,
    p.name AS product_name,
    c.name AS category_name,
    s.name AS supplier_name,
    p.quantity_in_stock,
    p.unit_cost,
    p.unit_price,
    ROUND(p.quantity_in_stock * p.unit_cost, 2) AS total_inventory_value
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id;

-- Low Stock Reorder Report
CREATE VIEW IF NOT EXISTS v_low_stock_alerts AS
SELECT
    product_id,
    sku,
    name AS product_name,
    quantity_in_stock
FROM products
WHERE quantity_in_stock < 10;

-- ============================================================================
-- SQL TRIGGERS (AUTOMATED STOCK UPDATES & INTEGRITY ENFORCEMENT)
-- ============================================================================

-- Prevent selling stock if current stock is insufficient

DROP TRIGGER IF EXISTS trg_prevent_negative_stock;
CREATE TRIGGER IF NOT EXISTS trg_prevent_negative_stock
BEFORE INSERT ON stock_movements
FOR EACH ROW
WHEN NEW.movement_type = 'OUT' AND (
    (SELECT quantity_in_stock FROM products WHERE product_id = NEW.product_id) < NEW.quantity
)
BEGIN
    SELECT RAISE(ABORT, 'Erro: Insufficient stock available for this transaction.');
END;

-- Automatically INCREASE stock when an 'IN' movement is recorded
DROP TRIGGER IF EXISTS trg_update_stock_after_in;
CREATE TRIGGER IF NOT EXISTS trg_update_stock_after_in
AFTER INSERT ON stock_movements
FOR EACH ROW
WHEN NEW.movement_type = 'IN'
BEGIN
    UPDATE products
    SET quantity_in_stock = quantity_in_stock + NEW.quantity
    WHERE product_id = NEW.product_id;
END;

-- Automatically DECREASE stock when an 'OUT' movement is recorded
DROP TRIGGER IF EXISTS trg_update_stock_after_out;
CREATE TRIGGER IF NOT EXISTS trg_update_stock_after_out
AFTER INSERT ON stock_movements
FOR EACH ROW
WHEN NEW.movement_type = 'OUT'
BEGIN
    UPDATE products
    SET quantity_in_stock = quantity_in_stock - NEW.quantity
    WHERE product_id = NEW.product_id;
END;