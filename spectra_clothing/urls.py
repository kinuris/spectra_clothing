"""
URL configuration for spectra_clothing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib import messages

def home_redirect(request):
    return redirect('dashboard:dashboard')

def custom_404_handler(request, exception):
    """Custom 404 handler that redirects based on authentication status"""
    if request.user.is_authenticated:
        messages.error(request, 'The page you requested does not exist. You have been redirected to the dashboard.')
        return redirect('dashboard:dashboard')
    else:
        messages.warning(request, 'Please log in to access the system.')
        return redirect('accounts:login')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('orders/', include('orders.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Custom error handlers
handler404 = custom_404_handler

# Add media URL for development
if settings.DEBUG:
    # Serve static files with Cache-Control header to prevent browser caching
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0], 
                         headers={'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'})
