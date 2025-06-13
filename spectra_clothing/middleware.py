from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404
from django.contrib import messages
from django.http import Http404

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


class AuthenticationMiddleware:
    """
    Middleware to handle authentication requirements for all routes.
    Ensures unauthenticated users are redirected to login for ANY route.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # List of paths that don't require authentication
        public_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Check if the current path is public
        is_public = any(request.path.startswith(path) for path in public_paths)
        
        # If user is not authenticated and trying to access ANY protected route
        if not request.user.is_authenticated and not is_public:
            messages.warning(request, 'Please log in to access the system.')
            return redirect(reverse('accounts:login'))
        
        response = self.get_response(request)
        return response


class PageNotFoundMiddleware:
    """
    Middleware to handle 404 errors and non-existent routes based on authentication status.
    - Authenticated users accessing non-existent routes → redirect to dashboard
    - Unauthenticated users accessing any route → redirect to login
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip static and media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # Check if the URL exists by trying to resolve it
        try:
            resolve(request.path)
        except Resolver404:
            # URL doesn't exist - handle based on authentication status
            if request.user.is_authenticated:
                # Authenticated user accessing non-existent route - redirect to dashboard
                messages.error(request, 'The page you requested does not exist. You have been redirected to the dashboard.')
                return redirect('dashboard:dashboard')
            else:
                # Unauthenticated user - redirect to login
                messages.warning(request, 'Please log in to access the system.')
                return redirect(reverse('accounts:login'))
        
        response = self.get_response(request)
        
        # Handle 404 responses that might occur during view processing
        if response.status_code == 404:
            if request.user.is_authenticated:
                messages.error(request, 'The page you requested does not exist. You have been redirected to the dashboard.')
                return redirect('dashboard:dashboard')
            else:
                messages.warning(request, 'Please log in to access the system.')
                return redirect(reverse('accounts:login'))
        
        return response
