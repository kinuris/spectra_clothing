from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('add/', views.supplier_add, name='supplier_add'),
    path('<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),
]
