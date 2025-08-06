from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('search/', views.search_view, name='search'),
    path('api/search/', views.search_api, name='search_api'),
] 