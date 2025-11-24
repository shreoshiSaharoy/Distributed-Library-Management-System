# # portal/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.search, name='search'),
#     path('register/', views.register, name='register'),
#     path('login/', views.login_view, name='login'),
#     path('download/<int:book_id>/', views.download_book, name='download'),
#     path('admin/login/', views.admin_login, name='admin_login'),
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/add_user/', views.admin_add_user, name='admin_add_user'),
#     path('admin/remove_user/<str:institute_id>/', views.admin_remove_user, name='admin_remove_user'),
#     path('admin/upload_book/', views.upload_book, name='upload_book'),
# ]


# # portal/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     # Main app
#     path('', views.search, name='search'),                 # default homepage = search page
#     path('search/', views.search, name='search'),

#     # Student auth
#     path('register/', views.register, name='register'),
#     path('login/', views.login_view, name='login'),

#     # Book downloading
#     path('download/<uuid:book_uuid>/', views.download_book, name='download'),

#     # Admin auth
#     path('admin/login/', views.admin_login, name='admin_login'),

#     # Admin dashboard
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

#     # Admin — manage users
#     path('admin/add_user/', views.admin_add_user, name='admin_add_user'),
#     path('admin/remove_user/<str:institute_id>/', views.admin_remove_user, name='admin_remove_user'),

#     # Admin — upload book
#     path('admin/upload_book/', views.upload_book, name='upload_book'),
# ]

# portal/urls.py
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
