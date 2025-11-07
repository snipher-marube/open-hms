from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Include app URLs
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('inventory/', include('inventory.urls')),
    path('reports/', include('core.urls')),
]