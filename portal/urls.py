from django.urls import path
from . import views

urlpatterns = [
    # HOME PAGE
    path('', views.home, name='home'),

    # Student auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    # Search
    path('search/', views.search, name='search'),

    # Downloading
    path('download/<uuid:book_uuid>/', views.download_book, name='download'),

    # Admin
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add_user/', views.admin_add_user, name='admin_add_user'),
    path('admin/remove_user/<str:institute_id>/', views.admin_remove_user, name='admin_remove_user'),
    path('admin/upload_book/', views.upload_book, name='upload_book'),
]
