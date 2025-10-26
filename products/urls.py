from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products, name='get_products'),
    path('product/<int:id>/', views.get_single_product, name='get_single_product'),
    path('addupdateproduct/', views.add_or_update_product, name='add_products'),
    path('deleteproduct/<int:product_id>/', views.delete_product, name='delete_product'),

]