from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleBasedAccessMiddleware:
    """
    Middleware to control access to views based on user roles.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Code to be executed for each request before the view is called
        
        # If user is not authenticated and trying to access a protected URL, redirect to login
        if not request.user.is_authenticated and not request.path.startswith('/admin/') and not request.path.startswith('/accounts/login/'):
            if request.path != '/' and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                messages.warning(request, 'Please log in to access that page.')
                return redirect(reverse('accounts:login'))
        
        # If user is authenticated, check role-based permissions
        if request.user.is_authenticated:
            # Admin can access everything
            if request.user.is_admin:
                pass
            
            # Stock Manager restrictions
            elif request.user.is_stock_manager:
                if (request.path.startswith('/accounts/users/') or 
                    request.path.startswith('/dashboard/reports/')):
                    messages.error(request, 'You do not have permission to access that page.')
                    return redirect('dashboard:dashboard')
            
            # Sales Staff restrictions
            elif request.user.is_sales:
                if (request.path.startswith('/accounts/users/') or 
                    request.path.startswith('/dashboard/reports/') or
                    request.path.startswith('/suppliers/')):
                    messages.error(request, 'You do not have permission to access that page.')
                    return redirect('dashboard:dashboard')
        
        response = self.get_response(request)
        return response
