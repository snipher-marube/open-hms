from django.urls import path
from . import views

urlpatterns = [
    # Inventory management
    path('', views.inventory_list, name='inventory-list'),
    path('create/', views.inventory_create, name='inventory-create'),
    path('<int:pk>/', views.inventory_detail, name='inventory-detail'),
    path('<int:pk>/update/', views.inventory_update, name='inventory-update'),
    path('<int:pk>/delete/', views.inventory_delete, name='inventory-delete'),
    
    # Stock transactions
    path('transactions/create/', views.stock_transaction_create, name='stock-transaction-create'),
    
    # Alerts and reports
    path('low-stock/', views.low_stock_items, name='low-stock-items'),
    path('expired/', views.expired_items, name='expired-items'),
    path('near-expiry/', views.near_expiry_items, name='near-expiry-items'),
    path('alerts/', views.stock_alerts, name='stock-alerts'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve-alert'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier-list'),
    path('suppliers/create/', views.supplier_create, name='supplier-create'),
    
    # Dashboard and analytics
    path('dashboard/', views.inventory_dashboard, name='inventory-dashboard'),
    
    # API endpoints
    path('api/item/<int:item_id>/', views.get_inventory_item_details, name='api-inventory-item-details'),
    path('api/check-stock/', views.check_stock_availability, name='api-check-stock'),

    # AJAX endpoints
    path('ajax/search-medicines/', views.ajax_search_medicines, name='ajax-search-medicines'),
    path('ajax/search-categories/', views.ajax_search_categories, name='ajax-search-categories'),
    path('ajax/search-suppliers/', views.ajax_search_suppliers, name='ajax-search-suppliers'),
    path('ajax/create-medicine/', views.ajax_create_medicine, name='ajax-create-medicine'),
    path('ajax/create-category/', views.ajax_create_category, name='ajax-create-category'),
    path('ajax/create-supplier/', views.ajax_create_supplier, name='ajax-create-supplier'),
]