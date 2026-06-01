from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.package_list, name='list'),
    path('ata/', views.assign_package, name='assign'),
    path('<int:pk>/duzenle/', views.edit_package, name='edit'),
    path('<int:pk>/devre-disi/', views.deactivate_package, name='deactivate'),
    path('<int:pk>/sil/', views.delete_package, name='delete'),
    path('paketlerim/', views.my_packages, name='my_packages'),
]
