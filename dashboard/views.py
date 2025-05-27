from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from .models import SalesReport, TopSellingProduct
from orders.models import Order, OrderItem
from products.models import Product
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
    # Get sales by month for the last 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    
    # Prepare data for charts
    context = {
        # Additional analytics data would go here
    }
    
    return render(request, 'dashboard/analytics.html', context)
