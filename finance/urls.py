from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.transaction_list, name='list'),
    path('ekle/', views.transaction_create, name='create'),
    path('<int:pk>/duzenle/', views.transaction_edit, name='edit'),
    path('<int:pk>/sil/', views.transaction_delete, name='delete'),
]
