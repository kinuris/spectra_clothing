def user_permissions(request):
    """
    Add user role-based permissions to the template context for menu rendering.
    """
    context = {
        'can_manage_users': False,
        'can_manage_products': False,
        'can_manage_inventory': False,
        'can_manage_orders': False,
        'can_manage_suppliers': False,
        'can_view_reports': False,
    }
    
    if request.user.is_authenticated:
        # Admin can do everything
        if request.user.is_admin:
            context = {k: True for k in context}
        
        # Stock manager can manage products, inventory, and suppliers
        elif request.user.is_stock_manager:
            context.update({
                'can_manage_products': True,
                'can_manage_inventory': True,
                'can_manage_suppliers': True,
            })
        
        # Sales staff can manage orders
        elif request.user.is_sales:
            context.update({
                'can_manage_orders': True,
            })
    
    return context
