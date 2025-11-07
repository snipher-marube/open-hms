from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Sum, F, Value, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import json

from .models import InventoryItem, StockTransaction, Supplier, Category, StockAlert, PurchaseOrder
from .forms import (
    InventoryItemForm, StockTransactionForm, SupplierForm, CategoryForm,
    PurchaseOrderForm, PurchaseOrderItemForm, InventorySearchForm, MedicineForm
)
from core.models import Clinic

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@require_http_methods(["GET"])
def ajax_search_medicines(request):
    query = request.GET.get('q', '')
    medicines = Medicine.objects.filter(name__icontains=query)[:10]
    results = [{'id': med.id, 'text': f"{med.name} ({med.generic_name})"} for med in medicines]
    return JsonResponse({'results': results})

@require_http_methods(["GET"])
def ajax_search_categories(request):
    query = request.GET.get('q', '')
    categories = Category.objects.filter(name__icontains=query)[:10]
    results = [{'id': cat.id, 'text': cat.name} for cat in categories]
    return JsonResponse({'results': results})

@require_http_methods(["GET"])
def ajax_search_suppliers(request):
    query = request.GET.get('q', '')
    suppliers = Supplier.objects.filter(name__icontains=query, is_active=True)[:10]
    results = [{'id': sup.id, 'text': sup.name} for sup in suppliers]
    return JsonResponse({'results': results})

@require_http_methods(["POST"])
def ajax_create_medicine(request):
    try:
        name = request.POST.get('name')
        generic_name = request.POST.get('generic_name', '')
        manufacturer = request.POST.get('manufacturer', '')
        description = request.POST.get('description', '')
        dosage_form = request.POST.get('dosage_form', '')
        strength = request.POST.get('strength', '')
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Medicine name is required'})
        
        medicine = Medicine.objects.create(
            name=name,
            generic_name=generic_name,
            manufacturer=manufacturer,
            description=description,
            dosage_form=dosage_form,
            strength=strength
        )
        
        return JsonResponse({
            'success': True,
            'object': {
                'id': medicine.id,
                'text': f"{medicine.name} ({medicine.generic_name})"
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def ajax_create_category(request):
    try:
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name is required'})
        
        category = Category.objects.create(
            name=name,
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'object': {
                'id': category.id,
                'text': category.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def ajax_create_supplier(request):
    try:
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Supplier name is required'})
        if not phone:
            return JsonResponse({'success': False, 'error': 'Phone number is required'})
        
        supplier = Supplier.objects.create(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'object': {
                'id': supplier.id,
                'text': supplier.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def inventory_list(request):
    form = InventorySearchForm(request.GET or None)
    items = InventoryItem.objects.select_related('medicine', 'supplier', 'category')
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        low_stock = form.cleaned_data.get('low_stock')
        near_expiry = form.cleaned_data.get('near_expiry')
        
        if search:
            items = items.filter(
                Q(medicine__name__icontains=search) |
                Q(medicine__generic_name__icontains=search) |
                Q(batch_number__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        if category:
            items = items.filter(category=category)
        
        if status:
            items = items.filter(status=status)
        
        if low_stock:
            items = items.filter(quantity__lte=F('min_stock_level'))
        
        if near_expiry:
            threshold_date = timezone.now().date() + timedelta(days=30)
            items = items.filter(
                expiry_date__lte=threshold_date,
                expiry_date__gte=timezone.now().date()
            )
    
    # Order by expiry date (soonest first) and then by quantity (lowest first)
    items = items.order_by('expiry_date', 'quantity')
    
    # Pagination
    paginator = Paginator(items, 25)  # 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Generate alerts
    generate_stock_alerts()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_items': items.count(),
        'total_value': InventoryItem.get_total_inventory_value(),
        'low_stock_count': InventoryItem.get_low_stock_items().count(),
        'expired_count': InventoryItem.get_expired_items().count(),
        'near_expiry_count': InventoryItem.get_near_expiry_items().count(),
    }
    
    return render(request, 'inventory/inventory_list.html', context)

@login_required
@permission_required('inventory.add_inventoryitem')
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            try:
                inventory_item = form.save()
                
                # Create initial stock transaction if quantity > 0
                if inventory_item.quantity > 0:
                    StockTransaction.objects.create(
                        inventory_item=inventory_item,
                        transaction_type='purchase',
                        quantity=inventory_item.quantity,
                        unit_price=inventory_item.cost_price,
                        reference='Initial Stock',
                        notes='Initial inventory setup',
                        created_by=request.user
                    )
                
                messages.success(request, f'Inventory item "{inventory_item.medicine.name}" created successfully.')
                return redirect('inventory-list')
            
            except Exception as e:
                messages.error(request, f'Error creating inventory item: {str(e)}')
    else:
        form = InventoryItemForm()
    
    # Create form instances for modals
    medicine_form = MedicineForm()
    category_form = CategoryForm()
    supplier_form = SupplierForm()
    
    return render(request, 'inventory/inventory_form.html', {
        'form': form,
        'medicine_form': medicine_form,
        'category_form': category_form,
        'supplier_form': supplier_form,
        'title': 'Add Inventory Item'
    })

@login_required
@permission_required('inventory.change_inventoryitem')
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inventory item "{item.medicine.name}" updated successfully.')
            return redirect('inventory-list')
    else:
        form = InventoryItemForm(instance=item)
    
    return render(request, 'inventory/inventory_form.html', {
        'form': form,
        'title': 'Update Inventory Item',
        'item': item
    })

@login_required
@permission_required('inventory.delete_inventoryitem')
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        item_name = item.medicine.name
        item.delete()
        messages.success(request, f'Inventory item "{item_name}" deleted successfully.')
        return redirect('inventory-list')
    
    return render(request, 'inventory/inventory_confirm_delete.html', {'item': item})

@login_required
def inventory_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    transactions = item.transactions.all().order_by('-transaction_date')[:20]
    
    # Usage statistics
    six_months_ago = timezone.now() - timedelta(days=180)
    usage_data = item.transactions.filter(
        transaction_type='sale',
        transaction_date__gte=six_months_ago
    ).extra({
        'month': "strftime('%%Y-%%m', transaction_date)"
    }).values('month').annotate(total_sold=Sum('quantity'))
    
    context = {
        'item': item,
        'transactions': transactions,
        'usage_data': json.dumps(list(usage_data)),
        'monthly_usage': item.get_usage_rate(),
    }
    
    return render(request, 'inventory/inventory_detail.html', context)

@login_required
def stock_transaction_create(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.created_by = request.user
                transaction.save()
                
                messages.success(request, f'Stock transaction recorded successfully.')
                return redirect('inventory-list')
            
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
    
    else:
        form = StockTransactionForm()
    
    return render(request, 'inventory/stock_transaction_form.html', {
        'form': form,
        'title': 'Record Stock Transaction'
    })

@login_required
def low_stock_items(request):
    items = InventoryItem.get_low_stock_items().select_related('medicine', 'supplier')
    return render(request, 'inventory/low_stock_items.html', {'items': items})

@login_required
def expired_items(request):
    items = InventoryItem.get_expired_items().select_related('medicine', 'supplier')
    return render(request, 'inventory/expired_items.html', {'items': items})

@login_required
def near_expiry_items(request):
    items = InventoryItem.get_near_expiry_items().select_related('medicine', 'supplier')
    return render(request, 'inventory/near_expiry_items.html', {'items': items})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier-list')
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'title': 'Add Supplier'
    })

@login_required
def inventory_dashboard(request):
    """Advanced inventory dashboard with analytics"""
    # Key metrics
    total_items = InventoryItem.objects.filter(status='active').count()
    total_value = InventoryItem.get_total_inventory_value()
    low_stock_count = InventoryItem.get_low_stock_items().count()
    expired_count = InventoryItem.get_expired_items().count()
    near_expiry_count = InventoryItem.get_near_expiry_items().count()
    
    # Top moving items
    thirty_days_ago = timezone.now() - timedelta(days=30)
    top_moving = StockTransaction.objects.filter(
        transaction_type='sale',
        transaction_date__gte=thirty_days_ago
    ).values('inventory_item__medicine__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:10]
    
    # Category distribution
    category_distribution = InventoryItem.objects.filter(
        status='active'
    ).values('category__name').annotate(
        total_items=Count('id'),
        total_value=Sum(F('quantity') * F('cost_price'))
    ).order_by('-total_value')
    
    # Expiry timeline
    expiry_timeline = InventoryItem.objects.filter(
        status='active',
        expiry_date__gte=timezone.now().date()
    ).extra({
        'month': "strftime('%%Y-%%m', expiry_date)"
    }).values('month').annotate(
        items_expiring=Count('id'),
        value_expiring=Sum(F('quantity') * F('cost_price'))
    ).order_by('month')[:12]
    
    context = {
        'total_items': total_items,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
        'near_expiry_count': near_expiry_count,
        'top_moving': top_moving,
        'category_distribution': category_distribution,
        'expiry_timeline': expiry_timeline,
    }
    
    return render(request, 'inventory/inventory_dashboard.html', context)

def generate_stock_alerts():
    """Generate stock alerts for low stock, expired, and near-expiry items"""
    # Clear unresolved alerts for items that are no longer in alert state
    StockAlert.objects.filter(is_resolved=False).delete()
    
    # Generate low stock alerts
    low_stock_items = InventoryItem.get_low_stock_items()
    for item in low_stock_items:
        severity = 'critical' if item.quantity == 0 else 'high'
        StockAlert.objects.create(
            inventory_item=item,
            alert_type='low_stock',
            severity=severity,
            message=f'Low stock alert: {item.medicine.name} has only {item.quantity} units left (min: {item.min_stock_level}).'
        )
    
    # Generate expired item alerts
    expired_items = InventoryItem.get_expired_items()
    for item in expired_items:
        StockAlert.objects.create(
            inventory_item=item,
            alert_type='expired',
            severity='critical',
            message=f'Expired item: {item.medicine.name} (Batch: {item.batch_number}) expired on {item.expiry_date}.'
        )
    
    # Generate near-expiry alerts
    near_expiry_items = InventoryItem.get_near_expiry_items()
    for item in near_expiry_items:
        days_until_expiry = (item.expiry_date - timezone.now().date()).days
        severity = 'high' if days_until_expiry <= 7 else 'medium'
        StockAlert.objects.create(
            inventory_item=item,
            alert_type='near_expiry',
            severity=severity,
            message=f'Near expiry: {item.medicine.name} (Batch: {item.batch_number}) expires in {days_until_expiry} days.'
        )

@login_required
def stock_alerts(request):
    alerts = StockAlert.objects.filter(is_resolved=False).select_related('inventory_item')
    return render(request, 'inventory/stock_alerts.html', {'alerts': alerts})

@login_required
def resolve_alert(request, alert_id):
    alert = get_object_or_404(StockAlert, id=alert_id)
    if request.method == 'POST':
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, 'Alert resolved successfully.')
    
    return redirect('stock-alerts')

# API endpoints for AJAX requests
@login_required
def get_inventory_item_details(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    data = {
        'id': item.id,
        'medicine_name': item.medicine.name,
        'batch_number': item.batch_number,
        'current_stock': item.quantity,
        'cost_price': str(item.cost_price),
        'selling_price': str(item.selling_price),
        'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
    }
    return JsonResponse(data)

@login_required
def check_stock_availability(request):
    item_id = request.GET.get('item_id')
    quantity = int(request.GET.get('quantity', 0))
    
    item = get_object_or_404(InventoryItem, id=item_id)
    available = item.quantity >= quantity
    
    return JsonResponse({
        'available': available,
        'current_stock': item.quantity,
        'message': f'Available: {item.quantity}' if available else f'Insufficient stock. Available: {item.quantity}'
    })