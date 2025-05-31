from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.product_add, name='product_add'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('<int:product_id>/force-update/', views.product_force_update, name='product_force_update'),
    path('<int:product_id>/simple-edit/', views.product_simple_edit, name='product_simple_edit'),
    path('<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('image/<int:image_id>/delete/', views.product_image_delete, name='product_image_delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
]
