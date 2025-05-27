from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Supplier
from products.models import Product

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        suppliers = suppliers.filter(name__icontains=search_query) | suppliers.filter(contact_person__icontains=search_query)
    
    # Pagination
    paginator = Paginator(suppliers, 10)  # Show 10 suppliers per page
    page = request.GET.get('page')
    try:
        suppliers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        suppliers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        suppliers = paginator.page(paginator.num_pages)
    
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'is_paginated': suppliers.has_other_pages(),
        'page_obj': suppliers,
        'paginator': paginator,
    }
    
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    # Get products associated with this supplier
    products = Product.objects.filter(supplier=supplier).order_by('name')
    
    context = {
        'supplier': supplier,
        'products': products,
    }
    
    return render(request, 'suppliers/supplier_detail.html', context)

@login_required
def supplier_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address', '')
        
        if not name or not contact_person or not email or not phone_number:
            messages.error(request, 'All fields except address are required.')
        else:
            try:
                supplier = Supplier.objects.create(
                    name=name,
                    contact_person=contact_person,
                    email=email,
                    phone_number=phone_number,
                    address=address
                )
                messages.success(request, f'Supplier {name} created successfully.')
                return redirect('suppliers:supplier_detail', supplier_id=supplier.id)
            except Exception as e:
                messages.error(request, f'Error creating supplier: {str(e)}')
    
    return render(request, 'suppliers/supplier_form.html')

@login_required
def supplier_edit(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address', '')
        
        if not name or not contact_person or not email or not phone_number:
            messages.error(request, 'All fields except address are required.')
        else:
            try:
                supplier.name = name
                supplier.contact_person = contact_person
                supplier.email = email
                supplier.phone_number = phone_number
                supplier.address = address
                supplier.save()
                
                messages.success(request, f'Supplier {name} updated successfully.')
                return redirect('suppliers:supplier_detail', supplier_id=supplier.id)
            except Exception as e:
                messages.error(request, f'Error updating supplier: {str(e)}')
    
    return render(request, 'suppliers/supplier_form.html', {'supplier': supplier})

@login_required
def supplier_delete(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        try:
            # Check if supplier has products
            products_count = Product.objects.filter(supplier=supplier).count()
            if products_count > 0:
                messages.error(request, f'Cannot delete supplier because {products_count} products are associated with it.')
                return redirect('suppliers:supplier_detail', supplier_id=supplier.id)
            
            supplier_name = supplier.name
            supplier.delete()
            messages.success(request, f'Supplier {supplier_name} deleted successfully.')
            return redirect('suppliers:supplier_list')
        except Exception as e:
            messages.error(request, f'Error deleting supplier: {str(e)}')
            return redirect('suppliers:supplier_detail', supplier_id=supplier.id)
    
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})
