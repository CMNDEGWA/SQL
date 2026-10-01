from django.db import models

class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'

class Suppliers(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact_email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suppliers'

class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    sku = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, blank=True, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, blank=True, null=True)
    unit_cost = models.FloatField()
    unit_price = models.FloatField()
    quantity_in_stock = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'

class StockMovements(models.Model):
    movement_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=10)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stock_movements'

# Django Model for your Database View
class VInventorySummary(models.Model):
    product_id = models.IntegerField(primary_key=True)
    sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    category_name = models.CharField(max_length=255)
    supplier_name = models.CharField(max_length=255)
    quantity_in_stock = models.IntegerField()
    unit_cost = models.FloatField()
    unit_price = models.FloatField()
    total_inventory_value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'v_inventory_summary'