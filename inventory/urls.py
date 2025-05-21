from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_overview, name='overview'),
    path('variants/', views.variant_list, name='variant_list'),
    path('variants/add/', views.variant_add, name='variant_add'),
    path('variants/<int:variant_id>/', views.variant_detail, name='variant_detail'),
    path('variants/<int:variant_id>/edit/', views.variant_edit, name='variant_edit'),
    path('variants/<int:variant_id>/delete/', views.variant_delete, name='variant_delete'),
    
    # Inventory Adjustment URLs
    path('adjustments/', views.adjustment_list, name='adjustment_list'),
    path('adjustments/add/', views.adjustment_add, name='adjustment_add'),
    
    # Size and Color Management
    path('sizes/', views.size_list, name='size_list'),
    path('sizes/add/', views.size_add, name='size_add'),
    path('sizes/<int:size_id>/edit/', views.size_edit, name='size_edit'),
    path('sizes/<int:size_id>/delete/', views.size_delete, name='size_delete'),
    
    path('colors/', views.color_list, name='color_list'),
    path('colors/add/', views.color_add, name='color_add'),
    path('colors/<int:color_id>/edit/', views.color_edit, name='color_edit'),
    path('colors/<int:color_id>/delete/', views.color_delete, name='color_delete'),
    
    # AJAX endpoints
    path('api/product-variants/', views.get_product_variants, name='get_product_variants'),
]
