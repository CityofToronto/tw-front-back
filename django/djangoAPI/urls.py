from django.urls import path
from . import views

urlpatterns = [
    path('db-init/', views.init_db),
    path('db-fill/', views.db_fill),
    path('db-update/', views.update_asset_role),
    path('test/', views.test),
    path('init-all', views.init_all),
    path('update-app', views.update_webapp),
    path('get-app', views.get_webapp),
]
