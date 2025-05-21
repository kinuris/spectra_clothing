from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product, Category, ProductImage
from suppliers.models import Supplier
from inventory.models import ProductVariant, Size, Color
import os

@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
    categories = Category.objects.all()
    
    # Filter by category if requested
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(sku__icontains=search_query)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)
    
    context = {
        'product': product,
        'variants': variants,
    }
    
    return render(request, 'products/product_detail.html', context)

@login_required
def product_add(request):
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        description = request.POST.get('description')
        
        # Validate data
        if Product.objects.filter(sku=sku).exists():
            messages.error(request, f'Product with SKU {sku} already exists.')
        else:
            try:
                # Create product
                product = Product.objects.create(
                    name=name,
                    sku=sku,
                    category_id=category_id,
                    supplier_id=supplier_id if supplier_id else None,
                    cost_price=cost_price,
                    selling_price=selling_price,
                    description=description
                )
                
                # Handle images
                images = request.FILES.getlist('images')
                for index, image in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_primary=(index == 0)  # First image is primary
                    )
                
                messages.success(request, f'Product {name} created successfully.')
                return redirect('products:product_detail', product_id=product.id)
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
    
    context = {
        'categories': categories,
        'suppliers': suppliers,
    }
    
    return render(request, 'products/product_form.html', context)

@login_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        description = request.POST.get('description')
        
        # Validate data
        if Product.objects.filter(sku=sku).exclude(id=product_id).exists():
            messages.error(request, f'Another product with SKU {sku} already exists.')
        else:
            try:
                # Update product
                product.name = name
                product.sku = sku
                product.category_id = category_id
                product.supplier_id = supplier_id if supplier_id else None
                product.cost_price = cost_price
                product.selling_price = selling_price
                product.description = description
                product.save()
                
                # Handle images
                images = request.FILES.getlist('images')
                for index, image in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_primary=False  # New images are not primary by default
                    )
                
                messages.success(request, f'Product {name} updated successfully.')
                return redirect('products:product_detail', product_id=product.id)
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
    
    context = {
        'product': product,
        'categories': categories,
        'suppliers': suppliers,
    }
    
    return render(request, 'products/product_form.html', context)

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            product_name = product.name
            product.delete()
            messages.success(request, f'Product {product_name} deleted successfully.')
            return redirect('products:product_list')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('products:product_detail', product_id=product.id)
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if Category.objects.filter(name=name).exists():
            messages.error(request, f'Category {name} already exists.')
        else:
            Category.objects.create(name=name, description=description)
            messages.success(request, f'Category {name} created successfully.')
            return redirect('products:category_list')
    
    return render(request, 'products/category_form.html')

@login_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            messages.error(request, f'Another category with name {name} already exists.')
        else:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, f'Category {name} updated successfully.')
            return redirect('products:category_list')
    
    return render(request, 'products/category_form.html', {'category': category})

@login_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        try:
            category_name = category.name
            category.delete()
            messages.success(request, f'Category {category_name} deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
        
        return redirect('products:category_list')
    
    return render(request, 'products/category_confirm_delete.html', {'category': category})
