from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products, name='get_products'),
    path('product/<int:id>/', views.get_single_product, name='get_single_product'),
    path('addproduct/', views.add_products, name='add_products'),
]