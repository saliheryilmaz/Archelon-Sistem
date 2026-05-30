from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', include('accounts.urls')),
    path('paket/', include('packages.urls')),
    path('randevu/', include('appointments.urls')),
    path('finans/', include('finance.urls')),
]
