from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('payorder/', views.razor_payment, name='razor_payment'),
    path('payvalid/', views.payment_validation, name='payment_validation'),
]