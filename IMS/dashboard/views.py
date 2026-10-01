from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import DatabaseError
from django.db.models import Case, F, IntegerField, Sum, Value, When
from django.db.models.functions import TruncDate
from .models import Products, StockMovements, VInventorySummary
from .forms import ProductForm, StockMovementForm

LOW_STOCK_THRESHOLD = 10

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
    low_stock_items = Products.objects.filter(quantity_in_stock__lte=LOW_STOCK_THRESHOLD)
    inventory_summary = VInventorySummary.objects.all()
    
    total_value = Products.objects.aggregate(
        total=Sum(F('quantity_in_stock') * F('unit_cost'))
    )['total'] or 0.0

    daily_movement_totals = (
        StockMovements.objects
        .annotate(movement_day=TruncDate('created_at'))
        .values('movement_day')
        .annotate(
            net_change=Sum(
                Case(
                    When(movement_type='IN', then=F('quantity')),
                    When(movement_type='OUT', then=-F('quantity')),
                    When(movement_type='ADJUSTMENT', then=F('quantity')),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        )
        .order_by('movement_day')
    )
    stock_trend_labels = []
    stock_trend_values = []
    running_stock = 0
    for movement_day in daily_movement_totals:
        if movement_day['movement_day'] is None:
            continue
        running_stock += movement_day['net_change'] or 0
        stock_trend_labels.append(movement_day['movement_day'].isoformat())
        stock_trend_values.append(running_stock)

    category_value_rows = (
        Products.objects
        .values('category__name')
        .annotate(value=Sum(F('quantity_in_stock') * F('unit_cost')))
        .order_by('category__name')
    )
    category_value_labels = []
    category_value_data = []
    for category in category_value_rows:
        value = category['value'] or 0
        if value <= 0:
            continue
        category_value_labels.append(category['category__name'] or 'Uncategorized')
        category_value_data.append(round(value, 2))

    recent_movements = StockMovements.objects.select_related('product').order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_items.count(),
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
        'total_value': round(total_value, 2),
        'stock_trend_labels': stock_trend_labels,
        'stock_trend_values': stock_trend_values,
        'category_value_labels': category_value_labels,
        'category_value_data': category_value_data,
        'inventory_summary': inventory_summary,
        'recent_movements': recent_movements,
        'product_form': product_form,
        'movement_form': movement_form,
    }
    return render(request, 'dashboard/index.html', context)