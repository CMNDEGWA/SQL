# SQL
All my studies on SQL, through Simple SQL Projects

## Inventory Management System IMS

An Inventory Management System (IMS) is a software application designed to track goods, stock levels, purchases and sales
across a business.
IMS uses a Relational Database to ensure accurate stock counts, track item movements, manage vendor details and prevent stockouts.

In a Relational Database, an IMS relies on interconnected tables;

- **Products**: Stores item details (SKU, Product name, Unit cost, Selling price, Current Stock Quantity).
- **Categories**: Group items logically.
- **Suppliers**: Track vendor details for restocking orders.
- **Stock Movements/Transactions**: Logs every instance stock increases or decreases.

![Relational Database tables linked by Foreign Key Relationship](../images/Relational%20Database.jpg)

### Project Roadmap

**Step 1**:
## Database Schemea Design and Data Definition Language.

This defines how tables, columns and relationships are structured  before any records are stored.
Four interconnected tables form the core model: **Categories, Suppliers, Products** and **Stock Movements or Transactions**.

- **Primary Key (PRIMARY KEY)**: A unique identifier assigned to every row (product_id) that prevents duplicate records.
- **Foreign Key (FOREIGN KEY)**: A reference column that points to the **PRIMARY KEY** of another table (linking product to its category).
- **Constraints**: Database-level rules that keep data accurate:
    - **NOT NULL**: Ensures a field cannot be left empty.
    - **UNIQUE**: Prevents duplicate values.
    - **CHECK**: Verifies that values meet specific logic rules.
    - **DEFAULT**: Fills in a default value if none is provided during insertion.
- **Data Types**:
    - **INTEGER**: Whole numbers (IDs, quantities).
    - **REAL**: Floating-point numbers (prices, monetary values).
    - **TEXT**: String values (names, descriptions, SKUs).
    - **DATETIME**: Timestamps.


**Step 2**: Data Insertion and Querying.

Populating sample inventory data using **INSERT** and retrieving it using **SELECT, WHERE** and **ORDER BY**.

**Step 3**: Relational Queries and Aggregations.

Joining tables using **INNER JOIN** and calculating stock value using **GROUP BY, SUM()** and **COUNT()**.

**Step 4**: Data Intergrity and Business Logic.

Enforcing business rues using **CONSTRAINTS** (e.g **CHECK (quantity >= 0)**), foreign key cascades and database triggers.
