from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import User
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        # Pass 'request' for AuthenticationForm's context, and 'data' for POST data.
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            # AuthenticationForm's is_valid() also checks credentials.
            # form.get_user() returns the authenticated user.
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful.')
            
            # Redirect to the 'next' page if provided, otherwise to a default.
            next_page = request.POST.get('next') or request.GET.get('next')
            if next_page:
                # In a production environment, you should validate 'next_page'
                # to prevent open redirect vulnerabilities.
                # from django.utils.http import url_has_allowed_host_and_scheme
                # if url_has_allowed_host_and_scheme(url=next_page, allowed_hosts={request.get_host()}):
                # return HttpResponseRedirect(next_page)
                return HttpResponseRedirect(next_page)
            return redirect('dashboard:dashboard')  # Default redirect target
        else:
            # Form is invalid (e.g., fields missing, or authentication failed).
            # AuthenticationForm adds appropriate error messages to form.errors.
            # This message serves as a general indicator.
            messages.error(request, 'Invalid username or password.')
    else:  # GET request
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('username')
    
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'is_paginated': users.has_other_pages(),
        'page_obj': users,
        'paginator': paginator,
    }
    
    return render(request, 'accounts/user_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_add(request):
    if request.method == 'POST':
        # Process form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            messages.success(request, f'User {username} created successfully.')
            return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_form.html', {'is_add': True})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Process form data
        user_obj.username = request.POST.get('username')
        user_obj.email = request.POST.get('email')
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.role = request.POST.get('role')
        
        password = request.POST.get('password')
        if password:
            user_obj.set_password(password)
        
        user_obj.save()
        messages.success(request, f'User {user_obj.username} updated successfully.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_form.html', {'user_obj': user_obj, 'is_add': False})

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user_obj.username
        if user_obj == request.user:
            messages.error(request, 'You cannot delete your own account.')
        else:
            user_obj.delete()
            messages.success(request, f'User {username} deleted successfully.')
        
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user_obj': user_obj})
