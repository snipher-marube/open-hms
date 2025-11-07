from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient-list'),
    path('create/', views.patient_create, name='patient-create'),
    path('<int:pk>/', views.patient_detail, name='patient-detail'),
    path('<int:pk>/update/', views.patient_update, name='patient-update'),
    path('<int:pk>/delete/', views.patient_delete, name='patient-delete'),
    path('<int:pk>/medical-records/', views.medical_record_list, name='medical-record-list'),
    path('<int:pk>/medical-records/create/', views.medical_record_create, name='medical-record-create'),
]