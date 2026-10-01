from django.shortcuts import render
from django.db.models import Sum, Count, F
from .models import Products, StockMovements, VInventorySummary

def inventory_dashboard(request):
    # Summary Metrics
    total_products = Products.objects.count()
    low_stock_items = Products.objects.filter(quantity_in_stock__lte=10)
    
    # Database View
    inventory_summary = VInventorySummary.objects.all()
    
    # Total valuation calcualtion using ORM aggregate
    total_value = Products.objects.aggregate(
        total = Sum(F('quantity_in_stock') * F('unit_cost'))
    )['total'] or 0.0
    
    # Recent Transactions audit trail
    recent_movements = StockMovements.objects.select_related('product').order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_items.count(),
        'total_value': round(total_value, 2),
        'inventory_summary': inventory_summary,
        'low_stock_items': low_stock_items,
        'recent_movements': recent_movements,
    }
    return render(request, 'dashboard/index.html', context)