from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_or_update_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = quantity
    cart_item.save()

    return Response({"message": "Cart updated successfully"}, status=200)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_item(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return Response({"error": "Cart not found"}, status=404)

    CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    return Response({"message": "Item removed successfully"}, status=200)
