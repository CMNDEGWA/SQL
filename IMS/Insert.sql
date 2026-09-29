-- Foreign Key Constraints enforcement in SQLite
PRAGMA foreign_keys = ON;

-- Data into Categories Table
INSERT OR IGNORE INTO Categories (name, description) VALUES
('Electronics','Computers, Electronic Devices, Accessories and Gadgets'),
('Books','All Literature Categories, Newspapers, Magazines, Journals and Comics'),
('Farm','Agricultural Equipment, Fertilizers, Seeds and Vaccines'),
('Services','Electrical, Mounting, Maintenance, and Harvesting Services');

-- Data into Suppliers Table
INSERT OR IGNORE INTO Suppliers (name, contact_email, phone, address) VALUES
('AgriTech Supplies','contact@agritechsupplies.com','+254 700 000 000','123 AgriTech Street, Nairobi, Kenya'),
('TechWorld Electronics','contact@techworldelectronics.com','+254 700 000 001','456 TechWorld Avenue, Nairobi, Kenya'),
('Book Haven','contact@bookhaven.com','+254 700 000 002','789 Book Haven Lane, Nairobi, Kenya');

-- Data into Products Table
-- unit_cost, unit_price, quantity_in_stock, category_id and supplier_id
INSERT OR IGNORE INTO Products
	(sku, name, category_id, supplier_id, unit_cost, unit_price, quantity_in_stock)
VALUES
('ELEC001','Laptop',(SELECT category_id FROM Categories WHERE name = 'Electronics'),(SELECT supplier_id FROM Suppliers WHERE contact_email = 'contact@techworldelectronics.com'),500.00,700.00,50),
('ELEC002','Smartphone',(SELECT category_id FROM Categories WHERE name = 'Electronics'),(SELECT supplier_id FROM Suppliers WHERE contact_email = 'contact@techworldelectronics.com'),200.00,300.00,100),
('BOOK001','The Great Gatsby',(SELECT category_id FROM Categories WHERE name = 'Books'),(SELECT supplier_id FROM Suppliers WHERE contact_email = 'contact@bookhaven.com'),5.00,10.00,200),
('BOOK002','1984',(SELECT category_id FROM Categories WHERE name = 'Books'),(SELECT supplier_id FROM Suppliers WHERE contact_email = 'contact@bookhaven.com'),4.00,8.00,150),
('FARM001','Tractor',(SELECT category_id FROM Categories WHERE name = 'Farm'),(SELECT supplier_id FROM Suppliers WHERE contact_email = 'contact@agritechsupplies.com'),1500.00,2000.00,10),
('FARM002','Fertilizer',(SELECT category_id FROM Categories WHERE name = 'Farm'),(SELECT supplier_id FROM Suppliers WHERE contact_email = 'contact@agritechsupplies.com'),20.00,30.00,500);

-- Data into Stock Movements Table
WITH seed(sku, movement_type, quantity, notes) AS (
	VALUES
		('ELEC001', 'IN', 50, 'Initial stock for Laptop'),
		('ELEC002', 'IN', 100, 'Initial stock for Smartphone'),
		('BOOK001', 'IN', 200, 'Initial stock for The Great Gatsby'),
		('BOOK002', 'IN', 150, 'Initial stock for 1984'),
		('FARM001', 'IN', 10, 'Initial stock for Tractor'),
		('FARM002', 'IN', 500, 'Initial stock for Fertilizer')
)
INSERT INTO Stock_Movements (product_id, movement_type, quantity, notes)
SELECT Products.product_id, seed.movement_type, seed.quantity, seed.notes
FROM seed
JOIN Products ON Products.sku = seed.sku
WHERE NOT EXISTS (
	SELECT 1
	FROM Stock_Movements
	WHERE Stock_Movements.product_id = Products.product_id
	  AND Stock_Movements.movement_type = seed.movement_type
	  AND Stock_Movements.quantity = seed.quantity
	  AND Stock_Movements.notes = seed.notes
);
