-- Format settings for human-readable file output
.headers ON
.mode table
.output inventory_report.txt

.print ""
.print "============================================================================"
.print "1. BASIC RETRIEVAL QUERIES"
.print "============================================================================"

.print ""
.print "--- [Query 1.1] Retrieving All Products ---"
SELECT sku, name, unit_price, quantity_in_stock
FROM Products;

.print ""
.print "--- [Query 1.2] Low Stock Alert (Quantity <= 10) ---"
SELECT sku, name, quantity_in_stock
FROM Products
WHERE quantity_in_stock <= 10;

.print ""
.print "--- [Query 1.3] Category Search (Text Pattern Matching) ---"
SELECT name, description
FROM Categories
WHERE name LIKE '%Farm%' OR description LIKE '%Services%';

.print ""
.print "--- [Query 1.4] Price Range Filter ($20.00 - $100.00) ---"
SELECT name, unit_price, quantity_in_stock
FROM Products
WHERE unit_price BETWEEN 20.00 AND 100.00
ORDER BY unit_price DESC;

.print ""
.print "--- [Query 1.5] Top 3 Most Expensive Products ---"
SELECT name, unit_price
FROM Products
ORDER BY unit_price DESC
LIMIT 3;

.print ""
.print "============================================================================"
.print "2. RELATIONAL QUERIES (INNER JOIN & LEFT JOIN)"
.print "============================================================================"

.print ""
.print "--- [Scenario A] Complete Inventory Catalog ---"
SELECT 
    p.sku,
    p.name AS product_name,
    c.name AS category_name,
    s.name AS supplier_name,
    p.quantity_in_stock,
    p.unit_price
FROM products p
INNER JOIN categories c ON p.category_id = c.category_id
INNER JOIN suppliers s ON p.supplier_id = s.supplier_id
ORDER BY c.name ASC, p.name ASC;

.print ""
.print "--- [Scenario B] Transaction Audit Trail ---"
SELECT 
    sm.movement_id,
    sm.created_at,
    p.sku,
    p.name AS product_name,
    sm.movement_type,
    sm.quantity,
    sm.notes
FROM stock_movements sm
INNER JOIN products p ON sm.product_id = p.product_id
ORDER BY sm.created_at DESC;

.print ""
.print "--- [Scenario C] Category Audit (All Categories & Assigned Products) ---"
SELECT 
    c.category_id,
    c.name AS category_name,
    p.name AS product_name
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
ORDER BY c.name;

.print ""
.print "============================================================================"
.print "3. AGGREGATIONS & GROUPING (GROUP BY, SUM, COUNT, HAVING)"
.print "============================================================================"

.print ""
.print "--- [Scenario D] Category Financial Summary ---"
SELECT 
    c.name AS category_name,
    COUNT(p.product_id) AS total_products,
    COALESCE(SUM(p.quantity_in_stock), 0) AS total_units_in_stock,
    ROUND(COALESCE(SUM(p.quantity_in_stock * p.unit_cost), 0), 2) AS total_asset_value,
    ROUND(AVG(p.unit_price), 2) AS avg_selling_price
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
ORDER BY total_asset_value DESC;

.print ""
.print "--- [Scenario E] Supplier Risk Analysis ---"
SELECT 
    s.name AS supplier_name,
    COUNT(p.product_id) AS unique_items_supplied,
    SUM(p.quantity_in_stock) AS total_units_supplied,
    ROUND(SUM(p.quantity_in_stock * p.unit_cost), 2) AS capital_invested
FROM suppliers s
INNER JOIN products p ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id, s.name
ORDER BY capital_invested DESC;

.print ""
.print "--- [Scenario F] High-Volume Category Filter (> 10 Total Units) ---"
SELECT 
    c.name AS category_name,
    COUNT(p.product_id) AS product_types,
    SUM(p.quantity_in_stock) AS total_stock_count
FROM categories c
INNER JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
HAVING SUM(p.quantity_in_stock) > 10
ORDER BY total_stock_count DESC;