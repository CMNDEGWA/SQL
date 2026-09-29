-- Enable Foreign Key Constraints enforcement in SQLite
PRAGMA foreign_keys = ON;

-- Create Categories Table
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Create Supliers Table
CREATE TABLE IF NOT EXISTS Suppliers (
    suppliers_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_email TEXT UNIQUE,
    phone TEXT,
    address TEXT
);

-- Create Products Table
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER,
    supplier_id INTEGER,
    unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantity_in_stock >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Categories(categories_id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(suppliers_id) ON DELETE SET NULL
);

-- Create Stock Movements Table
CREATE TABLE IF NOT EXISTS Stock_Movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(products_id) ON DELETE CASCADE
);
