from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import DatabaseError
from django.db.models import Sum, F
from .models import Products, StockMovements, VInventorySummary
from .forms import ProductForm, StockMovementForm

def inventory_dashboard(request):
    product_form = ProductForm()
    movement_form = StockMovementForm()

    if request.method == 'POST':
        # Action 1: Processing New Product Addition
        if 'btn_add_product' in request.POST:
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                try:
                    product_form.save()
                    messages.success(request, "New product added successfully!")
                    return redirect('dashboard')
                except DatabaseError as e:
                    messages.error(request, f"Database Error: {e}")

        # Action 2: Processing Stock Movement (IN / OUT)
        elif 'btn_record_movement' in request.POST:
            movement_form = StockMovementForm(request.POST)
            if movement_form.is_valid():
                try:
                    # Database triggers fire automatically upon save()
                    movement_form.save()
                    messages.success(request, "Stock movement recorded successfully! Inventory levels updated automatically.")
                    return redirect('dashboard')
                except DatabaseError as e:
                    # Catches SQLite trigger 'RAISE(ABORT)' when stock is insufficient
                    messages.error(request, f"Transaction Rejected: {e}")

    # Aggregations & Query Sets for Dashboard UI
    total_products = Products.objects.count()
    low_stock_items = Products.objects.filter(quantity_in_stock__lte=10)
    inventory_summary = VInventorySummary.objects.all()
    
    total_value = Products.objects.aggregate(
        total=Sum(F('quantity_in_stock') * F('unit_cost'))
    )['total'] or 0.0

    recent_movements = StockMovements.objects.select_related('product').order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_items.count(),
        'total_value': round(total_value, 2),
        'inventory_summary': inventory_summary,
        'recent_movements': recent_movements,
        'product_form': product_form,
        'movement_form': movement_form,
    }
    return render(request, 'dashboard/index.html', context)