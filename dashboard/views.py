from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, F, FloatField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta, date
from .models import SalesReport, TopSellingProduct
from orders.models import Order, OrderItem
from products.models import Product, Category
from inventory.models import ProductVariant

@login_required
def dashboard_view(request):
    # Get orders from today
    today = timezone.now().date()
    today_orders = Order.objects.filter(order_date__date=today)
    
    # Calculate total sales for today
    total_sales_today = sum([order.total_amount for order in today_orders])
    # total_sales_today = 0
    
    # Get pending orders
    pending_orders = Order.objects.filter(status=Order.PENDING).count()
    
    # Get low stock items
    low_stock_items = ProductVariant.objects.filter(quantity__lte=5).count()
    
    # Get total products
    total_products = Product.objects.count()
    
    # Get recent orders (last 5)
    recent_orders = Order.objects.all().order_by('-order_date')[:5]
    
    # Get top selling products (based on last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    top_products = (
        OrderItem.objects.filter(order__order_date__gte=thirty_days_ago)
        .values('product_variant__product__name', 'product_variant__product__category__name')
        .annotate(total_quantity=Sum('quantity'), total_sales=Sum('price'))
        .order_by('-total_quantity')[:5]
    )
    
    context = {
        'total_sales_today': total_sales_today,
        'orders_today_count': today_orders.count(),
        'pending_orders': pending_orders,
        'low_stock_items': low_stock_items,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@login_required
def report_list(request):
    reports = SalesReport.objects.all().order_by('-generated_at')
    
    # Pagination
    paginator = Paginator(reports, 10)  # Show 10 reports per page
    page = request.GET.get('page')
    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        reports = paginator.page(1)
    except EmptyPage:
        reports = paginator.page(paginator.num_pages)
    
    context = {
        'reports': reports,
        'is_paginated': reports.has_other_pages(),
        'page_obj': reports,
        'paginator': paginator,
    }
    
    return render(request, 'dashboard/report_list.html', context)

@login_required
def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        # Validate dates
        try:
            date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to_obj = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Use YYYY-MM-DD.')
            return redirect('dashboard:report_list')
        
        if date_from_obj > date_to_obj:
            messages.error(request, 'Start date must be before end date.')
            return redirect('dashboard:report_list')
        
        # Get orders within date range
        orders = Order.objects.filter(
            order_date__date__gte=date_from_obj,
            order_date__date__lte=date_to_obj
        ).exclude(status=Order.CANCELLED)
        
        # Calculate totals
        total_orders = orders.count()
        total_sales = sum([order.total_amount for order in orders])
        
        # Calculate KPIs
        average_order_value = None
        if total_orders > 0:
            average_order_value = total_sales / total_orders
        
        # Create report
        report = SalesReport.objects.create(
            report_type=report_type,
            date_from=date_from_obj,
            date_to=date_to_obj,
            total_sales=total_sales,
            total_orders=total_orders,
            generated_by=request.user
        )
        
        # Get top selling products for this period
        top_products = (
            OrderItem.objects.filter(
                order__in=orders
            ).values(
                'product_variant__product'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_sales=Sum('price')
            ).order_by('-total_quantity')[:5]
        )
        
        # Add top products to report
        for item in top_products:
            product = Product.objects.get(id=item['product_variant__product'])
            TopSellingProduct.objects.create(
                report=report,
                product=product,
                total_quantity=item['total_quantity'],
                total_sales=item['total_sales']
            )
        
        messages.success(request, f'{report.get_report_type_display()} report generated successfully.')
        return redirect('dashboard:report_detail', report_id=report.id)
    
    return render(request, 'dashboard/report_form.html')

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(SalesReport, id=report_id)
    
    # No need to calculate KPIs here as they're defined as properties in the SalesReport model
    # and will be calculated automatically when accessed in the template
    
    return render(request, 'dashboard/report_detail.html', {'report': report})

@login_required
def report_delete(request, report_id):
    report = get_object_or_404(SalesReport, id=report_id)
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Report deleted successfully.')
        return redirect('dashboard:report_list')
    
    return render(request, 'dashboard/report_confirm_delete.html', {'report': report})

@login_required
def analytics_view(request):
    try:
        # Get time period for filtering
        period_days = int(request.GET.get('period', 7))  # Default to 7 days
    except (ValueError, TypeError):
        period_days = 7

    # Handle custom date range if provided
    if request.GET.get('start_date') and request.GET.get('end_date'):
        try:
            period_start = timezone.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            period_end = timezone.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            # Calculate days for consistent period comparison
            period_days = (period_end - period_start).days + 1
        except ValueError:
            # Fall back to default if dates are invalid
            period_start = timezone.now().date() - timedelta(days=period_days-1)
            period_end = timezone.now().date()
    else:
        # Use default period
        period_start = timezone.now().date() - timedelta(days=period_days-1)
        period_end = timezone.now().date()

    # Get previous period for comparison
    prev_period_start = period_start - timedelta(days=period_days)
    prev_period_end = period_start - timedelta(days=1)
    
    # Get filtered orders
    current_orders = Order.objects.filter(
        order_date__date__gte=period_start,
        order_date__date__lte=period_end
    ).exclude(status=Order.CANCELLED)
    
    previous_orders = Order.objects.filter(
        order_date__date__gte=prev_period_start,
        order_date__date__lte=prev_period_end
    ).exclude(status=Order.CANCELLED)
    
    # Calculate sales metrics
    total_sales = sum([order.total_amount for order in current_orders])
    total_orders = current_orders.count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Calculate previous period metrics for comparison
    prev_total_sales = sum([order.total_amount for order in previous_orders])
    prev_total_orders = previous_orders.count()
    prev_avg_order_value = prev_total_sales / prev_total_orders if prev_total_orders > 0 else 0
    
    # Calculate change percentages
    sales_change_pct = ((total_sales - prev_total_sales) / prev_total_sales * 100) if prev_total_sales > 0 else 0
    orders_change_pct = ((total_orders - prev_total_orders) / prev_total_orders * 100) if prev_total_orders > 0 else 0
    aov_change_pct = ((avg_order_value - prev_avg_order_value) / prev_avg_order_value * 100) if prev_avg_order_value > 0 else 0
    
    # Get daily sales data for the chart
    daily_sales = {}
    
    # Generate all dates in the range to ensure no gaps
    current_date = period_start
    while current_date <= period_end:
        date_str = current_date.strftime('%Y-%m-%d')
        daily_sales[date_str] = 0  # Initialize with zero
        current_date += timedelta(days=1)
    
    # Fill in the actual sales data
    for order in current_orders:
        order_date = order.order_date.date().strftime('%Y-%m-%d')
        if order_date in daily_sales:
            daily_sales[order_date] += order.total_amount
    
    # Sort by date
    daily_sales_sorted = {k: daily_sales[k] for k in sorted(daily_sales.keys())}
    
    # Get top products data
    top_products = (
        OrderItem.objects.filter(order__in=current_orders)
        .values('product_variant__product__id', 'product_variant__product__name')
        .annotate(
            units_sold=Sum('quantity'),
            revenue=Sum('price')
        )
        .order_by('-revenue')[:5]
    )
    
    # Get sales by category
    category_sales = (
        OrderItem.objects.filter(order__in=current_orders)
        .values('product_variant__product__category__name')
        .annotate(
            orders=Count('order', distinct=True),
            units=Sum('quantity'),
            revenue=Sum('price')
        )
        .order_by('-revenue')
    )
    
    # Calculate total for percentages
    total_revenue = sum(item['revenue'] for item in category_sales) if category_sales else 0
    
    # Add percentage to each category
    for item in category_sales:
        if total_revenue > 0:
            item['percentage'] = round((item['revenue'] / total_revenue) * 100, 1)
        else:
            item['percentage'] = 0
    
    context = {
        'period_days': period_days,
        'period_start': period_start,
        'period_end': period_end,
        'prev_period_start': prev_period_start,
        'prev_period_end': prev_period_end,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'prev_total_sales': prev_total_sales,
        'prev_total_orders': prev_total_orders,
        'prev_avg_order_value': prev_avg_order_value,
        'sales_change_pct': sales_change_pct,
        'orders_change_pct': orders_change_pct,
        'aov_change_pct': aov_change_pct,
        'daily_sales_data': daily_sales_sorted,
        'top_products': top_products,
        'category_sales': category_sales,
    }
    
    return render(request, 'dashboard/analytics.html', context)
