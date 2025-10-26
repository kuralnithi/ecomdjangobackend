from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cart, name='get_cart'),
    path('add-or-update/', views.add_or_update_cart, name='add_or_update_cart'),
    path('clear/<int:product_id>/', views.remove_item, name='remove_item'),
]
