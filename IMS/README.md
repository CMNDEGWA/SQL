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

**Step 2**: 
## Data Insertion and Querying.

**Data Manipilation Language** (DML) handles populating, retrieving and modifying data inside existing tables. Populating the Inventory Management System (IMS) with product records and wrte queries to retrieve, filter and sort inventory data.

The core SQL Data Operations:
- **INSERT INTO**: Adds new rows to a table. Targeting columns and matching values.
- **SELECT**: Retrieves columns from one or more tables. Using * selects all columns, while naming specific columns optimizes performance.
- **WHERE**: Filters records based on logicl conditions. **(=, >, <, >=, <=, !=, LIKE, IN, AND, OR)**.
- **ORDER BY**: Sorts out records in ascending **(ASC, default)** or descending **(DESC)** order.
- **Calculated Columns**: Performs arithmetic direcly inside the query. **((unit_price - unit_cost) AS profit_margin)**.

**Step 3**: 
## Relational Queries and Aggregations.

They transform raw normalised tables into meaningful business metrics, such as total_stock value, supplier dependence and category performance.

The core SQL Joining and Aggregation CCOncepts:
- **INNER JOIN**: Matches rows from two or more tables where the join condition is met. If a product has no assigned category, it will not appear in an **INNER JOIN** between **Products** and **Categories**.
- **LEFT JOIN(OUTER JOIN)**: Retrieves all rows from the primary (left) table, even if there are no matching records in the joined (right) table. This is essential for dicovering categories with zero products or products with no transactional history.
- **Table Alias(p,c,s,sm)**: Short names assigned to tables in the **FROM** clause to keep multi-table queries readable and avoid typing long table names.
- **GROUP BY**: Collapses multiple rows with identical values in specified columns into summary rows.
- **Aggregate Functions**:
    - **COUNT()**: Counts the number of rows or non-null column values.
    - **SUM()**: Adds up numeric values accross grouped rows.
    - **AVG()**: Calculates the mean value across grouped rows.
- **HAVING Clause**: Filters aggregated groups after the **GROUP BY** calculation takes place. (Unlike **WHERE**, which filters individual rows before grouping occurs).

**Step 4**: Data Intergrity and Business Logic.

Enforcing business rues using **CONSTRAINTS** (e.g **CHECK (quantity >= 0)**), foreign key cascades and database triggers.
