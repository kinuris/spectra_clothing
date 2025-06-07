from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        products = products.filter(name__icontains=search_query)
    
    # Pagination
    paginator = Paginator(products, 10)  # Show 10 items per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'is_paginated': products.has_other_pages(),
        'page_obj': products,
        'paginator': paginator,
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
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        description = request.POST.get('description')
        
        # Validate data
        if Product.objects.filter(name=name).exists():
            messages.error(request, f'Product with name "{name}" already exists.')
        else:
            try:
                # Create product
                product = Product.objects.create(
                    name=name,
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
    
    # Log all request info for debugging
    print("==== PRODUCT EDIT - DEBUG INFO ====")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"Content type: {request.content_type}")
    print(f"Content type header: {request.headers.get('Content-Type')}")
    print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
    
    # Debug headers that might be impacting form submission
    print("=== Request Headers ===")
    for header, value in request.headers.items():
        print(f"{header}: {value}")
    print("======================")
    
    print(f"Request POST data: {list(request.POST.items())}")
    print(f"Request FILES: {list(request.FILES.items())}")
    print(f"Request body size: {len(request.body)} bytes")
    print("==== END DEBUG INFO ====")
    
    # Check if this is a direct update request
    direct_update = request.POST.get('direct_submit') == 'true'
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        description = request.POST.get('description')
        primary_image_id = request.POST.get('primary_image')
        
        # Debug message to track form submission data
        print(f"Product Edit - Form Data: name={name}, primary_image={primary_image_id}")
        
        # Validate data
        if Product.objects.filter(name=name).exclude(id=product_id).exists():
            messages.error(request, f'Another product with name "{name}" already exists.')
        else:
            try:
                # Update product
                product.name = name
                product.category_id = category_id
                product.supplier_id = supplier_id if supplier_id else None
                product.cost_price = cost_price
                product.selling_price = selling_price
                product.description = description
                product.save()
                
                # Handle primary image selection
                if primary_image_id:
                    # Reset all images to non-primary
                    ProductImage.objects.filter(product=product).update(is_primary=False)
                    
                    # Set the selected image as primary
                    try:
                        primary_image = ProductImage.objects.get(id=primary_image_id, product=product)
                        primary_image.is_primary = True
                        primary_image.save()
                    except ProductImage.DoesNotExist:
                        # If we can't find the primary image, select the first one as primary
                        first_image = ProductImage.objects.filter(product=product).first()
                        if first_image:
                            first_image.is_primary = True
                            first_image.save()
                
                # Handle new images
                images = request.FILES.getlist('images')
                
                # If we have images to add
                if images:
                    for index, image in enumerate(images):
                        # Set as primary only if there are no primary images yet
                        is_primary = not ProductImage.objects.filter(product=product, is_primary=True).exists()
                        
                        ProductImage.objects.create(
                            product=product,
                            image=image,
                            is_primary=is_primary
                        )
                
                # Ensure at least one image is set as primary
                if not ProductImage.objects.filter(product=product, is_primary=True).exists():
                    first_image = ProductImage.objects.filter(product=product).first()
                    if first_image:
                        first_image.is_primary = True
                        first_image.save()
                
                messages.success(request, f'Product {name} updated successfully.')
                return redirect('products:product_detail', product_id=product.id)
            except Exception as e:
                import traceback
                print(f"Error updating product: {str(e)}")
                print(traceback.format_exc())  # Get detailed traceback for debugging
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
def product_simple_edit(request, product_id):
    """
    A special simplified edit page that focuses just on basic fields with a cleaner form
    """
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    
    context = {
        'product': product,
        'categories': categories,
        'suppliers': suppliers,
    }
    
    return render(request, 'products/simple_update_form.html', context)

@login_required
def product_force_update(request, product_id):
    """
    Enhanced simplified view for product updates that now supports image uploads.
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Debug the incoming request
    print("==== FORCE UPDATE REQUEST ====")
    print(f"Method: {request.method}")
    print(f"Content type: {request.content_type}")
    print(f"Encoding: {request.encoding}")
    print(f"POST data: {list(request.POST.items())}")
    print(f"FILES data: {list(request.FILES.items())}")
    print(f"Request headers: {dict(request.headers)}")
    print("================================")
    
    if request.method == 'POST':
        try:
            # Get basic required fields
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            cost_price = request.POST.get('cost_price')
            selling_price = request.POST.get('selling_price')
            
            # Get optional fields
            supplier_id = request.POST.get('supplier')
            description = request.POST.get('description', '')
            primary_image_id = request.POST.get('primary_image')
            
            # Basic validation for required fields
            if not all([name, category_id, cost_price, selling_price]):
                messages.error(request, 'Required fields are missing.')
                return redirect('products:product_edit', product_id=product_id)
            
            # Check if product name exists on another product
            if Product.objects.filter(name=name).exclude(id=product_id).exists():
                messages.error(request, f'Another product with name "{name}" already exists.')
                return redirect('products:product_edit', product_id=product_id)
            
            # Update product - core fields only in this simplified version
            product.name = name
            product.category_id = category_id
            product.supplier_id = supplier_id if supplier_id else None
            product.cost_price = cost_price
            product.selling_price = selling_price
            product.description = description
            product.save()
            
            # Handle image uploads - enhanced implementation
            images = request.FILES.getlist('images')
            print(f"FILES object contains: {request.FILES.keys()}")
            print(f"Images list from getlist: {images}")
            
            if images:
                print(f"Processing {len(images)} new image uploads")
                # Determine if this is the first image for the product
                has_existing_images = ProductImage.objects.filter(product=product).exists()
                print(f"Product has existing images: {has_existing_images}")
                
                for index, image_file in enumerate(images):
                    # First image should be primary if there are no other images
                    is_primary = (index == 0 and not has_existing_images)
                    print(f"Image {index + 1}: {image_file.name}, Size: {image_file.size} bytes, Primary: {is_primary}")
                    
                    try:
                        # Create the new product image
                        new_image = ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            is_primary=is_primary
                        )
                        print(f"Successfully created new image {new_image.id} for product {product.id}")
                    except Exception as e:
                        print(f"Error creating image: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
            
            # Update primary image if specified
            if primary_image_id:
                print(f"Primary image ID received: {primary_image_id}")
                # Reset all images
                ProductImage.objects.filter(product=product).update(is_primary=False)
                print("Reset all images to non-primary")
                
                # Set the selected one as primary
                try:
                    primary_image = ProductImage.objects.get(id=primary_image_id, product=product)
                    primary_image.is_primary = True
                    primary_image.save()
                    print(f"Successfully set image {primary_image_id} as primary")
                except ProductImage.DoesNotExist:
                    print(f"Could not find image {primary_image_id} for product {product.id}")
                    # If primary image wasn't found, set the first image as primary
                    first_image = ProductImage.objects.filter(product=product).first()
                    if first_image:
                        first_image.is_primary = True
                        first_image.save()
                        print(f"Set first image {first_image.id} as primary instead")
            else:
                print("No primary image ID specified in request")
            
            # Ensure at least one image is primary if images exist
            if ProductImage.objects.filter(product=product).exists() and not ProductImage.objects.filter(product=product, is_primary=True).exists():
                first_image = ProductImage.objects.filter(product=product).first()
                first_image.is_primary = True
                first_image.save()
                print(f"Ensuring primary image: set {first_image.id} as primary")
            
            messages.success(request, f'Product {name} updated successfully.')
            return redirect('products:product_detail', product_id=product.id)
            
        except Exception as e:
            import traceback
            print(f"Error in force update: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('products:product_edit', product_id=product_id)
    
    # For GET requests, show the edit form
    return redirect('products:product_edit', product_id=product_id)

@login_required
def product_image_delete(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    
    # Handle setting a new primary image if needed
    is_primary = image.is_primary
    
    if request.method == 'POST':
        try:
            # Delete the image file
            if image.image:
                if os.path.isfile(image.image.path):
                    os.remove(image.image.path)
            
            # Delete the image record
            image.delete()
            
            # If this was the primary image, set a new primary if available
            if is_primary:
                remaining_images = ProductImage.objects.filter(product_id=product_id).first()
                if remaining_images:
                    remaining_images.is_primary = True
                    remaining_images.save()
            
            messages.success(request, 'Image deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting image: {str(e)}')
    
    return redirect('products:product_edit', product_id=product_id)

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(categories, 10)  # Show 10 items per page
    page = request.GET.get('page')
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'is_paginated': categories.has_other_pages(),
        'page_obj': categories,
        'paginator': paginator,
    }
    
    return render(request, 'products/category_list.html', context)

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
