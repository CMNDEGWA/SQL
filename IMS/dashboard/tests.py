import sqlite3
import tempfile
from pathlib import Path

from django.db import IntegrityError, connection
from django.test import TransactionTestCase

from migrate_inventory import migrate_database
from .forms import ProductForm, StockMovementForm
from .models import Products, StockMovements


IMS_ROOT = Path(__file__).resolve().parents[1]


class InventoryDatabaseTests(TransactionTestCase):
	reset_sequences = True

	def setUp(self):
		super().setUp()
		connection.ensure_connection()
		database = connection.connection
		database.executescript(
			"""
			DROP VIEW IF EXISTS v_low_stock_alerts;
			DROP VIEW IF EXISTS v_inventory_summary;
			DROP TABLE IF EXISTS Stock_Movements;
			DROP TABLE IF EXISTS Products;
			DROP TABLE IF EXISTS Suppliers;
			DROP TABLE IF EXISTS Categories;
			"""
		)
		for script_name in ("Schema.sql", "ViewsTriggers.sql", "Insert.sql"):
			database.executescript((IMS_ROOT / script_name).read_text(encoding="utf-8"))

	def test_seed_is_idempotent_and_opening_stock_is_not_doubled(self):
		laptop = Products.objects.get(sku="ELEC001")
		self.assertEqual(laptop.quantity_in_stock, 50)
		self.assertEqual(StockMovements.objects.filter(product=laptop).count(), 1)

		connection.connection.executescript((IMS_ROOT / "Insert.sql").read_text(encoding="utf-8"))

		laptop.refresh_from_db()
		self.assertEqual(laptop.quantity_in_stock, 50)
		self.assertEqual(StockMovements.objects.filter(product=laptop).count(), 1)

	def test_product_form_creates_products_with_zero_stock(self):
		form = ProductForm(data={
			"sku": "NEW-001",
			"name": "New item",
			"category": "",
			"supplier": "",
			"unit_cost": "2.50",
			"unit_price": "5.00",
		})
		self.assertNotIn("quantity_in_stock", form.fields)
		self.assertTrue(form.is_valid(), form.errors)

		product = form.save()

		self.assertEqual(product.quantity_in_stock, 0)
		self.assertFalse(StockMovements.objects.filter(product=product).exists())

	def test_in_out_and_signed_adjustments_update_stock(self):
		product = Products.objects.get(sku="ELEC001")
		movements = (
			("IN", 5),
			("OUT", 3),
			("ADJUSTMENT", 4),
			("ADJUSTMENT", -2),
		)
		for movement_type, quantity in movements:
			form = StockMovementForm(data={
				"product": product.product_id,
				"movement_type": movement_type,
				"quantity": quantity,
				"notes": "test movement",
			})
			self.assertTrue(form.is_valid(), form.errors)
			form.save()

		product.refresh_from_db()
		self.assertEqual(product.quantity_in_stock, 54)

	def test_movement_form_rejects_zero_and_nonpositive_regular_movements(self):
		product = Products.objects.get(sku="ELEC001")
		for movement_type, quantity in (("ADJUSTMENT", 0), ("IN", 0), ("OUT", -1)):
			form = StockMovementForm(data={
				"product": product.product_id,
				"movement_type": movement_type,
				"quantity": quantity,
				"notes": "invalid movement",
			})
			self.assertFalse(form.is_valid(), f"{movement_type} {quantity} should be invalid")

	def test_database_rejects_oversell_and_negative_adjustment(self):
		product = Products.objects.get(sku="FARM001")
		for movement_type, quantity in (("OUT", 11), ("ADJUSTMENT", -11)):
			form = StockMovementForm(data={
				"product": product.product_id,
				"movement_type": movement_type,
				"quantity": quantity,
				"notes": "must be rejected by trigger",
			})
			self.assertTrue(form.is_valid(), form.errors)
			with self.assertRaises(IntegrityError):
				form.save()

		product.refresh_from_db()
		self.assertEqual(product.quantity_in_stock, 10)

	def test_low_stock_view_includes_quantity_ten(self):
		product = Products.objects.get(sku="FARM001")
		with connection.cursor() as cursor:
			cursor.execute(
				"UPDATE products SET quantity_in_stock = 10 WHERE product_id = %s",
				[product.product_id],
			)
			cursor.execute(
				"SELECT COUNT(*) FROM v_low_stock_alerts WHERE product_id = %s",
				[product.product_id],
			)
			self.assertEqual(cursor.fetchone()[0], 1)

	def test_migration_preserves_rows_and_is_idempotent(self):
		with tempfile.TemporaryDirectory() as temporary_directory:
			database_path = Path(temporary_directory) / "legacy.db"
			with sqlite3.connect(database_path) as database:
				database.executescript(
					"""
					PRAGMA foreign_keys = ON;
					CREATE TABLE Products (
						product_id INTEGER PRIMARY KEY,
						sku TEXT NOT NULL,
						name TEXT NOT NULL,
						quantity_in_stock INTEGER NOT NULL DEFAULT 0
					);
					CREATE TABLE Stock_Movements (
						movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
						product_id INTEGER NOT NULL,
						movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT')),
						quantity INTEGER NOT NULL CHECK (quantity > 0),
						notes TEXT,
						created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
						FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
					);
					CREATE INDEX idx_stock_movements_product ON Stock_Movements(product_id);
					CREATE TRIGGER trg_legacy_audit AFTER INSERT ON Stock_Movements
					BEGIN SELECT 1; END;
					CREATE VIEW v_low_stock_alerts AS
					SELECT product_id, sku, name AS product_name, quantity_in_stock
					FROM Products WHERE quantity_in_stock < 10;
					INSERT INTO Products VALUES (7, 'LEGACY-001', 'Legacy item', 9);
					INSERT INTO Stock_Movements VALUES (21, 7, 'IN', 12, 'opening', '2026-09-01 00:00:00');
					INSERT INTO Stock_Movements VALUES (22, 7, 'OUT', 3, 'sale', '2026-09-02 00:00:00');
					"""
				)

			backup_path = migrate_database(database_path)

			self.assertTrue(backup_path.is_file())
			with sqlite3.connect(database_path) as database:
				self.assertEqual(
					database.execute(
						"SELECT movement_id, movement_type, quantity, notes FROM Stock_Movements ORDER BY movement_id"
					).fetchall(),
					[(21, "IN", 12, "opening"), (22, "OUT", 3, "sale")],
				)
				self.assertEqual(
					database.execute(
						"SELECT quantity_in_stock FROM Products WHERE product_id = 7"
					).fetchone()[0],
					9,
				)
				self.assertEqual(database.execute("PRAGMA foreign_key_check").fetchall(), [])
				self.assertEqual(
					database.execute(
						"SELECT 1 FROM sqlite_master WHERE type = 'index' "
						"AND name = 'idx_stock_movements_product'"
					).fetchone(),
					(1,),
				)
				self.assertEqual(
					database.execute(
						"SELECT 1 FROM sqlite_master WHERE type = 'trigger' "
						"AND name = 'trg_legacy_audit'"
					).fetchone(),
					(1,),
				)
				database.execute(
					"INSERT INTO Stock_Movements (product_id, movement_type, quantity, notes) "
					"VALUES (7, 'ADJUSTMENT', -2, 'count correction')"
				)
				self.assertEqual(
					database.execute(
						"SELECT quantity_in_stock FROM Products WHERE product_id = 7"
					).fetchone()[0],
					7,
				)
				self.assertEqual(
					database.execute(
						"SELECT COUNT(*) FROM v_low_stock_alerts WHERE product_id = 7"
					).fetchone()[0],
					1,
				)

			self.assertIsNone(migrate_database(database_path))
			self.assertEqual(len(list(Path(temporary_directory).glob("*.bak"))), 1)
