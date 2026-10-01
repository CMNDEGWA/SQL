"""Apply the signed-adjustment migration to an explicitly selected SQLite database."""

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


MIGRATION_NAME = "signed_adjustments_v1"
REPLACED_TRIGGERS = {
    "trg_prevent_negative_stock",
    "trg_update_stock_after_in",
    "trg_update_stock_after_out",
    "trg_prevent_negative_adjustment",
    "trg_update_stock_after_adjustment",
}

TRIGGERS = (
    """CREATE TRIGGER trg_prevent_negative_stock
    BEFORE INSERT ON stock_movements
    FOR EACH ROW
    WHEN NEW.movement_type = 'OUT' AND (
        (SELECT quantity_in_stock FROM products WHERE product_id = NEW.product_id) < NEW.quantity
    )
    BEGIN
        SELECT RAISE(ABORT, 'Error: Insufficient stock available for this transaction.');
    END""",
    """CREATE TRIGGER trg_prevent_negative_adjustment
    BEFORE INSERT ON stock_movements
    FOR EACH ROW
    WHEN NEW.movement_type = 'ADJUSTMENT' AND (
        (SELECT quantity_in_stock FROM products WHERE product_id = NEW.product_id) + NEW.quantity < 0
    )
    BEGIN
        SELECT RAISE(ABORT, 'Error: Adjustment would result in negative stock.');
    END""",
    """CREATE TRIGGER trg_update_stock_after_in
    AFTER INSERT ON stock_movements
    FOR EACH ROW
    WHEN NEW.movement_type = 'IN'
    BEGIN
        UPDATE products
        SET quantity_in_stock = quantity_in_stock + NEW.quantity
        WHERE product_id = NEW.product_id;
    END""",
    """CREATE TRIGGER trg_update_stock_after_out
    AFTER INSERT ON stock_movements
    FOR EACH ROW
    WHEN NEW.movement_type = 'OUT'
    BEGIN
        UPDATE products
        SET quantity_in_stock = quantity_in_stock - NEW.quantity
        WHERE product_id = NEW.product_id;
    END""",
    """CREATE TRIGGER trg_update_stock_after_adjustment
    AFTER INSERT ON stock_movements
    FOR EACH ROW
    WHEN NEW.movement_type = 'ADJUSTMENT'
    BEGIN
        UPDATE products
        SET quantity_in_stock = quantity_in_stock + NEW.quantity
        WHERE product_id = NEW.product_id;
    END""",
)


def _database_check(connection, pragma):
    result = connection.execute(pragma).fetchone()
    if result is None or result[0] != "ok":
        raise sqlite3.DatabaseError(f"Database check failed: {pragma}: {result}")


def _create_backup(database_path):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_path = database_path.with_name(
        f"{database_path.name}.pre_signed_adjustments_{timestamp}.bak"
    )
    with sqlite3.connect(database_path) as source, sqlite3.connect(backup_path) as backup:
        source.backup(backup)
    with sqlite3.connect(backup_path) as backup:
        _database_check(backup, "PRAGMA integrity_check")
    return backup_path


def migrate_database(database_path):
    database_path = Path(database_path).resolve()
    if not database_path.is_file():
        raise FileNotFoundError(f"Database does not exist: {database_path}")

    with sqlite3.connect(database_path) as connection:
        migration_table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ims_schema_migrations'"
        ).fetchone()
        if migration_table and connection.execute(
            "SELECT 1 FROM ims_schema_migrations WHERE name = ?", (MIGRATION_NAME,)
        ).fetchone():
            return None

        _database_check(connection, "PRAGMA integrity_check")
        if connection.execute("PRAGMA foreign_key_check").fetchone():
            raise sqlite3.IntegrityError("Database has foreign-key violations; migration stopped.")
        if not connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'Stock_Movements'"
        ).fetchone():
            raise sqlite3.DatabaseError("Stock_Movements table was not found.")

    backup_path = _create_backup(database_path)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS ims_schema_migrations ("
            "name TEXT PRIMARY KEY, applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        if connection.execute(
            "SELECT 1 FROM ims_schema_migrations WHERE name = ?", (MIGRATION_NAME,)
        ).fetchone():
            connection.rollback()
            return None

        indexes = [row[0] for row in connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'index' "
            "AND tbl_name = 'Stock_Movements' AND sql IS NOT NULL"
        )]
        custom_triggers = [
            (name, sql)
            for name, sql in connection.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type = 'trigger' AND tbl_name = 'Stock_Movements' AND sql IS NOT NULL"
            )
            if name not in REPLACED_TRIGGERS
        ]

        connection.execute(
            """CREATE TABLE Stock_Movements_new (
                movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT')),
                quantity INTEGER NOT NULL CHECK (
                    (movement_type = 'ADJUSTMENT' AND quantity <> 0)
                    OR (movement_type IN ('IN', 'OUT') AND quantity > 0)
                ),
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
            )"""
        )
        connection.execute(
            """INSERT INTO Stock_Movements_new
                (movement_id, product_id, movement_type, quantity, notes, created_at)
                SELECT movement_id, product_id, movement_type, quantity, notes, created_at
                FROM Stock_Movements"""
        )
        connection.execute("DROP TABLE Stock_Movements")
        connection.execute("ALTER TABLE Stock_Movements_new RENAME TO Stock_Movements")

        for index_sql in indexes:
            connection.execute(index_sql)
        for trigger_sql in TRIGGERS:
            connection.execute(trigger_sql)
        for _, trigger_sql in custom_triggers:
            connection.execute(trigger_sql)

        connection.execute("DROP VIEW IF EXISTS v_low_stock_alerts")
        connection.execute(
            """CREATE VIEW v_low_stock_alerts AS
                SELECT product_id, sku, name AS product_name, quantity_in_stock
                FROM products
                WHERE quantity_in_stock <= 10"""
        )
        connection.execute(
            "INSERT INTO ims_schema_migrations (name) VALUES (?)", (MIGRATION_NAME,)
        )

        _database_check(connection, "PRAGMA integrity_check")
        if connection.execute("PRAGMA foreign_key_check").fetchone():
            raise sqlite3.IntegrityError("Migration introduced foreign-key violations.")
        connection.commit()
        connection.execute("PRAGMA foreign_keys = ON")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return backup_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        required=True,
        type=Path,
        help="Explicit path to the SQLite database to migrate; a verified backup is created first.",
    )
    arguments = parser.parse_args()
    backup_path = migrate_database(arguments.database)
    if backup_path is None:
        print(f"Migration already applied to {arguments.database}.")
    else:
        print(f"Migration applied. Backup: {backup_path}")


if __name__ == "__main__":
    main()
