from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from .models import Size, Color, ProductVariant, InventoryAdjustment
from products.models import Product
from django.db.models import Sum
import json

@login_required
def inventory_overview(request):
    # Count total variants
    total_variants = ProductVariant.objects.count()
    
    # Count low stock variants
    low_stock_variants = ProductVariant.objects.filter(quantity__lte=5).count()
    
    # Count out of stock variants
    out_of_stock_variants = ProductVariant.objects.filter(quantity=0).count()
    
    # Get recent inventory adjustments
    recent_adjustments = InventoryAdjustment.objects.order_by('-created_at')[:10]
    
    context = {
        'total_variants': total_variants,
        'low_stock_variants': low_stock_variants,
        'out_of_stock_variants': out_of_stock_variants,
        'recent_adjustments': recent_adjustments,
    }
    
    return render(request, 'inventory/overview.html', context)

@login_required
def variant_list(request):
    variants = ProductVariant.objects.all().select_related('product', 'size', 'color')
    
    # Filter by product if requested
    product_id = request.GET.get('product')
    if product_id:
        variants = variants.filter(product_id=product_id)
    
    # Filter by stock level if requested
    stock_level = request.GET.get('stock_level')
    if stock_level == 'low':
        variants = variants.filter(quantity__lte=5, quantity__gt=0)
    elif stock_level == 'out':
        variants = variants.filter(quantity=0)
    
    # Get all products for filter dropdown
    products = Product.objects.all().order_by('name')
    
    context = {
        'variants': variants,
        'products': products,
        'selected_product': product_id,
        'selected_stock_level': stock_level,
    }
    
    return render(request, 'inventory/variant_list.html', context)

@login_required
def variant_detail(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    # Get adjustment history for this variant
    adjustments = InventoryAdjustment.objects.filter(variant=variant).order_by('-created_at')
    
    context = {
        'variant': variant,
        'adjustments': adjustments,
    }
    
    return render(request, 'inventory/variant_detail.html', context)

@login_required
def variant_add(request):
    products = Product.objects.all().order_by('name')
    sizes = Size.objects.all().order_by('name')
    colors = Color.objects.all().order_by('name')
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')
        quantity = request.POST.get('quantity', 0)
        reorder_level = request.POST.get('reorder_level', 5)
        
        # Check if variant already exists
        if ProductVariant.objects.filter(product_id=product_id, size_id=size_id, color_id=color_id).exists():
            messages.error(request, 'This product variant already exists.')
        else:
            try:
                variant = ProductVariant.objects.create(
                    product_id=product_id,
                    size_id=size_id,
                    color_id=color_id,
                    quantity=quantity,
                    reorder_level=reorder_level
                )
                
                # Create inventory adjustment record if initial quantity > 0
                if int(quantity) > 0:
                    InventoryAdjustment.objects.create(
                        variant=variant,
                        adjustment_type=InventoryAdjustment.INCOMING,
                        quantity=quantity,
                        notes='Initial inventory',
                        created_by=request.user
                    )
                
                messages.success(request, 'Product variant created successfully.')
                return redirect('inventory:variant_detail', variant_id=variant.id)
            except Exception as e:
                messages.error(request, f'Error creating variant: {str(e)}')
    
    context = {
        'products': products,
        'sizes': sizes,
        'colors': colors,
    }
    
    return render(request, 'inventory/variant_form.html', context)

@login_required
def variant_edit(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    if request.method == 'POST':
        reorder_level = request.POST.get('reorder_level', 5)
        
        try:
            variant.reorder_level = reorder_level
            variant.save()
            
            messages.success(request, 'Product variant updated successfully.')
            return redirect('inventory:variant_detail', variant_id=variant.id)
        except Exception as e:
            messages.error(request, f'Error updating variant: {str(e)}')
    
    return render(request, 'inventory/variant_form.html', {'variant': variant})

@login_required
def variant_delete(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    if request.method == 'POST':
        try:
            variant_name = f"{variant.product.name} - {variant.size.name} - {variant.color.name}"
            variant.delete()
            messages.success(request, f'Variant {variant_name} deleted successfully.')
            return redirect('inventory:variant_list')
        except Exception as e:
            messages.error(request, f'Error deleting variant: {str(e)}')
            return redirect('inventory:variant_detail', variant_id=variant.id)
    
    return render(request, 'inventory/variant_confirm_delete.html', {'variant': variant})

@login_required
def adjustment_list(request):
    adjustments = InventoryAdjustment.objects.all().order_by('-created_at')
    
    # Filter by product if requested
    product_id = request.GET.get('product')
    if product_id:
        adjustments = adjustments.filter(variant__product_id=product_id)
    
    # Filter by adjustment type if requested
    adjustment_type = request.GET.get('type')
    if adjustment_type:
        adjustments = adjustments.filter(adjustment_type=adjustment_type)
    
    # Get all products for filter dropdown
    products = Product.objects.all().order_by('name')
    
    context = {
        'adjustments': adjustments,
        'products': products,
        'selected_product': product_id,
        'selected_type': adjustment_type,
        'adjustment_types': InventoryAdjustment.ADJUSTMENT_TYPE_CHOICES,
    }
    
    return render(request, 'inventory/adjustment_list.html', context)

@login_required
def adjustment_add(request):
    products = Product.objects.all().order_by('name')
    
    if request.method == 'POST':
        variant_id = request.POST.get('variant')
        adjustment_type = request.POST.get('adjustment_type')
        quantity = int(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')
        
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than zero.')
        else:
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                
                # Update variant quantity based on adjustment type
                if adjustment_type == InventoryAdjustment.INCOMING:
                    variant.quantity += quantity
                elif adjustment_type == InventoryAdjustment.OUTGOING:
                    if variant.quantity < quantity:
                        messages.error(request, 'Not enough stock for this adjustment.')
                        return redirect('inventory:adjustment_add')
                    variant.quantity -= quantity
                elif adjustment_type == InventoryAdjustment.ADJUSTMENT:
                    # Direct adjustment to a specific value
                    variant.quantity = quantity
                
                variant.save()
                
                # Create adjustment record
                InventoryAdjustment.objects.create(
                    variant=variant,
                    adjustment_type=adjustment_type,
                    quantity=quantity,
                    notes=notes,
                    created_by=request.user
                )
                
                messages.success(request, 'Inventory adjustment created successfully.')
                return redirect('inventory:adjustment_list')
            except Exception as e:
                messages.error(request, f'Error creating adjustment: {str(e)}')
    
    context = {
        'products': products,
        'adjustment_types': InventoryAdjustment.ADJUSTMENT_TYPE_CHOICES,
    }
    
    return render(request, 'inventory/adjustment_form.html', context)

@login_required
def size_list(request):
    sizes = Size.objects.all().order_by('name')
    return render(request, 'inventory/size_list.html', {'sizes': sizes})

@login_required
def size_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if Size.objects.filter(name=name).exists():
            messages.error(request, f'Size {name} already exists.')
        else:
            Size.objects.create(name=name)
            messages.success(request, f'Size {name} created successfully.')
            return redirect('inventory:size_list')
    
    return render(request, 'inventory/size_form.html')

@login_required
def size_edit(request, size_id):
    size = get_object_or_404(Size, id=size_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if Size.objects.filter(name=name).exclude(id=size_id).exists():
            messages.error(request, f'Another size with name {name} already exists.')
        else:
            size.name = name
            size.save()
            messages.success(request, f'Size {name} updated successfully.')
            return redirect('inventory:size_list')
    
    return render(request, 'inventory/size_form.html', {'size': size})

@login_required
def size_delete(request, size_id):
    size = get_object_or_404(Size, id=size_id)
    
    if request.method == 'POST':
        try:
            size_name = size.name
            size.delete()
            messages.success(request, f'Size {size_name} deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting size: {str(e)}')
        
        return redirect('inventory:size_list')
    
    return render(request, 'inventory/size_confirm_delete.html', {'size': size})

@login_required
def color_list(request):
    colors = Color.objects.all().order_by('name')
    return render(request, 'inventory/color_list.html', {'colors': colors})

@login_required
def color_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color_code = request.POST.get('color_code')
        
        if Color.objects.filter(name=name).exists():
            messages.error(request, f'Color {name} already exists.')
        else:
            Color.objects.create(name=name, color_code=color_code)
            messages.success(request, f'Color {name} created successfully.')
            return redirect('inventory:color_list')
    
    return render(request, 'inventory/color_form.html')

@login_required
def color_edit(request, color_id):
    color = get_object_or_404(Color, id=color_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        color_code = request.POST.get('color_code')
        
        if Color.objects.filter(name=name).exclude(id=color_id).exists():
            messages.error(request, f'Another color with name {name} already exists.')
        else:
            color.name = name
            color.color_code = color_code
            color.save()
            messages.success(request, f'Color {name} updated successfully.')
            return redirect('inventory:color_list')
    
    return render(request, 'inventory/color_form.html', {'color': color})

@login_required
def color_delete(request, color_id):
    color = get_object_or_404(Color, id=color_id)
    
    if request.method == 'POST':
        try:
            color_name = color.name
            color.delete()
            messages.success(request, f'Color {color_name} deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting color: {str(e)}')
        
        return redirect('inventory:color_list')
    
    return render(request, 'inventory/color_confirm_delete.html', {'color': color})

# AJAX endpoint to get variants for a product
@login_required
def get_product_variants(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)
    
    variants = ProductVariant.objects.filter(product_id=product_id, quantity__gt=0)
    variant_data = [
        {
            'id': v.id,
            'size': v.size.name,
            'color': v.color.name,
            'quantity': v.quantity,
            'display': f"{v.size.name} / {v.color.name} ({v.quantity} in stock)",
            'product': {
                'id': v.product.id,
                'name': v.product.name,
                'price': v.product.selling_price,
                'sku': v.product.sku
            }
        }
        for v in variants
    ]
    
    return JsonResponse({'variants': variant_data})
