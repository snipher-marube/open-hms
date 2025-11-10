from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill-list'),
    path('create/', views.bill_create, name='bill-create'),
    path('<int:pk>/', views.bill_detail, name='bill-detail'),
    path('<int:pk>/initiate-stk-push/', views.initiate_stk_push, name='initiate-stk-push'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
]
