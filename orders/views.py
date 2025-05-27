from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Order, OrderItem, Customer
from products.models import Product
from inventory.models import ProductVariant, InventoryAdjustment
from django.db import transaction
import json
from decimal import Decimal

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    
    # Filter by status if requested
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by customer if requested
    customer_id = request.GET.get('customer')
    if customer_id:
        orders = orders.filter(customer_id=customer_id)
        
    # Search by order ID
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(id__icontains=search_query)
    
    # Get all customers for filter dropdown
    customers = Customer.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 items per page
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
        'customers': customers,
        'selected_status': status,
        'selected_customer': customer_id,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
        'is_paginated': orders.has_other_pages(),
        'page_obj': orders,
        'paginator': paginator,
    }
    
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('product_variant', 'product_variant__product', 'product_variant__size', 'product_variant__color')
    
    context = {
        'order': order,
        'items': items,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_add(request):
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        
        # Create customer if it's a new one
        if customer_id == 'new':
            customer_name = request.POST.get('new_customer_name')
            customer_phone = request.POST.get('new_customer_phone')
            customer_email = request.POST.get('new_customer_email', '')
            customer_address = request.POST.get('new_customer_address', '')
            
            if not customer_name or not customer_phone:
                messages.error(request, 'Customer name and phone number are required.')
                return redirect('orders:order_add')
            
            customer = Customer.objects.create(
                name=customer_name,
                phone_number=customer_phone,
                email=customer_email,
                address=customer_address
            )
            customer_id = customer.id
        
        notes = request.POST.get('notes', '')
        
        # Get all product variant IDs and quantities
        variant_data = json.loads(request.POST.get('variant_data', '[]'))
        
        if not variant_data:
            messages.error(request, 'Please add at least one product to the order.')
            return redirect('orders:order_add')
        
        try:
            with transaction.atomic():
                # Create the order
                order = Order.objects.create(
                    customer_id=customer_id,
                    status=Order.PENDING,
                    notes=notes,
                    created_by=request.user
                )
                
                # Add order items
                for item in variant_data:
                    variant_id = item.get('variant_id')
                    quantity = int(item.get('quantity', 0))
                    
                    if quantity <= 0:
                        continue
                    
                    variant = ProductVariant.objects.get(id=variant_id)
                    
                    # Check inventory
                    if variant.quantity < quantity:
                        raise ValueError(f"Not enough stock for {variant.product.name} - {variant.size.name} - {variant.color.name}")
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product_variant=variant,
                        quantity=quantity,
                        price=variant.product.selling_price
                    )
                    
                    # Update inventory if order is not pending
                    if order.status != Order.PENDING:
                        # Reduce inventory
                        variant.quantity -= quantity
                        variant.save()
                        
                        # Create inventory adjustment record
                        InventoryAdjustment.objects.create(
                            variant=variant,
                            adjustment_type=InventoryAdjustment.OUTGOING,
                            quantity=quantity,
                            notes=f'Order #{order.id}',
                            created_by=request.user
                        )
                
                messages.success(request, f'Order #{order.id} created successfully.')
                return redirect('orders:order_detail', order_id=order.id)
        
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    context = {
        'customers': customers,
        'products': products,
    }
    
    return render(request, 'orders/order_form.html', context)

@login_required
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Only allow editing pending orders
    if order.status != Order.PENDING:
        messages.warning(request, f'Order #{order.id} is already in progress and cannot be edited.')
        return redirect('orders:order_detail', order_id=order.id)
    
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        notes = request.POST.get('notes', '')
        
        # Get all product variant IDs and quantities
        variant_data = json.loads(request.POST.get('variant_data', '[]'))
        
        if not variant_data:
            messages.error(request, 'Please add at least one product to the order.')
            return redirect('orders:order_edit', order_id=order.id)
        
        try:
            with transaction.atomic():
                # Update order details
                order.customer_id = customer_id
                order.notes = notes
                order.updated_by = request.user
                order.save()
                
                # Remove existing order items
                order.items.all().delete()
                
                # Add new order items
                for item in variant_data:
                    variant_id = item.get('variant_id')
                    quantity = int(item.get('quantity', 0))
                    
                    if quantity <= 0:
                        continue
                    
                    variant = ProductVariant.objects.get(id=variant_id)
                    
                    # Check inventory
                    if variant.quantity < quantity:
                        raise ValueError(f"Not enough stock for {variant.product.name} - {variant.size.name} - {variant.color.name}")
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product_variant=variant,
                        quantity=quantity,
                        price=variant.product.selling_price
                    )
                
                messages.success(request, f'Order #{order.id} updated successfully.')
                return redirect('orders:order_detail', order_id=order.id)
        
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')
    
    context = {
        'order': order,
        'customers': customers,
        'products': products,
    }
    
    return render(request, 'orders/order_form.html', context)

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            messages.error(request, 'Invalid order status.')
        else:
            old_status = order.status
            
            try:
                with transaction.atomic():
                    # Update order status
                    order.status = new_status
                    order.updated_by = request.user
                    order.save()
                    
                    # If changing from PENDING or CANCELLED to another status, reduce inventory
                    if (old_status in [Order.PENDING, Order.CANCELLED]) and new_status not in [Order.PENDING, Order.CANCELLED]:
                        for item in order.items.all():
                            variant = item.product_variant
                            
                            # Check inventory
                            if variant.quantity < item.quantity:
                                raise ValueError(f"Not enough stock for {variant.product.name} - {variant.size.name} - {variant.color.name}")
                            
                            # Reduce inventory
                            variant.quantity -= item.quantity
                            variant.save()
                            
                            # Create inventory adjustment record
                            InventoryAdjustment.objects.create(
                                variant=variant,
                                adjustment_type=InventoryAdjustment.OUTGOING,
                                quantity=item.quantity,
                                notes=f'Order #{order.id} - Status changed to {dict(Order.STATUS_CHOICES)[new_status]}',
                                created_by=request.user
                            )
                    
                    # If changing to CANCELLED and was not PENDING, restore inventory
                    elif new_status == Order.CANCELLED and old_status not in [Order.PENDING, Order.CANCELLED]:
                        for item in order.items.all():
                            variant = item.product_variant
                            
                            # Restore inventory
                            variant.quantity += item.quantity
                            variant.save()
                            
                            # Create inventory adjustment record
                            InventoryAdjustment.objects.create(
                                variant=variant,
                                adjustment_type=InventoryAdjustment.INCOMING,
                                quantity=item.quantity,
                                notes=f'Order #{order.id} - Cancelled',
                                created_by=request.user
                            )
                    
                    messages.success(request, f'Order status updated to {dict(Order.STATUS_CHOICES)[new_status]}.')
            
            except Exception as e:
                messages.error(request, f'Error updating order status: {str(e)}')
    
    return redirect('orders:order_detail', order_id=order.id)

@login_required
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Only allow deleting pending orders
    if order.status != Order.PENDING:
        messages.warning(request, f'Order #{order.id} is already in progress and cannot be deleted.')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        try:
            order_number = order.id
            order.delete()
            messages.success(request, f'Order #{order_number} deleted successfully.')
            return redirect('orders:order_list')
        except Exception as e:
            messages.error(request, f'Error deleting order: {str(e)}')
            return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/order_confirm_delete.html', {'order': order})

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(name__icontains=search_query) | customers.filter(phone_number__icontains=search_query)
    
    # Pagination
    paginator = Paginator(customers, 10)  # Show 10 items per page
    page = request.GET.get('page')
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    
    context = {
        'customers': customers,
        'search_query': search_query,
        'is_paginated': customers.has_other_pages(),
        'page_obj': customers,
        'paginator': paginator,
    }
    
    return render(request, 'orders/customer_list.html', context)

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    
    return render(request, 'orders/customer_detail.html', context)

@login_required
def customer_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        
        if not name or not phone_number:
            messages.error(request, 'Name and phone number are required.')
        else:
            try:
                customer = Customer.objects.create(
                    name=name,
                    phone_number=phone_number,
                    email=email,
                    address=address
                )
                messages.success(request, f'Customer {name} created successfully.')
                return redirect('orders:customer_detail', customer_id=customer.id)
            except Exception as e:
                messages.error(request, f'Error creating customer: {str(e)}')
    
    return render(request, 'orders/customer_form.html')

@login_required
def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        
        if not name or not phone_number:
            messages.error(request, 'Name and phone number are required.')
        else:
            try:
                customer.name = name
                customer.phone_number = phone_number
                customer.email = email
                customer.address = address
                customer.save()
                
                messages.success(request, f'Customer {name} updated successfully.')
                return redirect('orders:customer_detail', customer_id=customer.id)
            except Exception as e:
                messages.error(request, f'Error updating customer: {str(e)}')
    
    return render(request, 'orders/customer_form.html', {'customer': customer})

@login_required
def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        try:
            # Check if customer has orders
            if Order.objects.filter(customer=customer).exists():
                messages.error(request, f'Cannot delete customer {customer.name} because they have orders in the system.')
                return redirect('orders:customer_detail', customer_id=customer.id)
            
            customer_name = customer.name
            customer.delete()
            messages.success(request, f'Customer {customer_name} deleted successfully.')
            return redirect('orders:customer_list')
        except Exception as e:
            messages.error(request, f'Error deleting customer: {str(e)}')
            return redirect('orders:customer_detail', customer_id=customer.id)
    
    return render(request, 'orders/customer_confirm_delete.html', {'customer': customer})
