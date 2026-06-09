from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('giris/', views.login_view, name='login'),
    path('cikis/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('kullanicilar/', views.user_list, name='user_list'),
    path('kullanicilar/yeni/', views.user_create, name='user_create'),
    path('kullanicilar/<int:pk>/duzenle/', views.user_edit, name='user_edit'),
    path('kullanicilar/<int:pk>/sil/', views.user_delete, name='user_delete'),
    path('kullanicilar/<int:pk>/karne/', views.user_report, name='user_report'),
]
