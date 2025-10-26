from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_products(request):
    try:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({
            'message': 'get products working',
            'products': serializer.data
        })
    except Exception as e:
        return Response(
            {'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_single_product(request, id):
    try:
        product = Product.objects.get(id=id)
        serializer = ProductSerializer(product)
        return Response({
            'message': 'get single products working',
            'product': serializer.data
        })
    except Product.DoesNotExist:
        return Response(
            {'message': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'message': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_or_update_product(request):
    """
    Adds a new product or updates an existing product by productid (primary key).
    If 'id' is provided in the request, updates the existing record. If not, a new product is created.
    """
    try:
        product_id = request.data.get('id')
        data = request.data.copy()

        if product_id:
            # Try to update using the product's primary key
            product, created = Product.objects.update_or_create(
                id=product_id,
                defaults=data
            )
        else:
            # Create a new product if no id is provided
            product = Product.objects.create(**data)
            created = True

        serializer = ProductSerializer(product)
        message = 'Product updated successfully' if not created else 'Product added successfully'

        return Response({
            'message': message,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'message': 'Error adding/updating product', 'data': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    try:
        # Try to get the product by ID
        product = Product.objects.get(id=product_id)
        product.delete()

        return Response(
            {'message': 'Product deleted successfully'},
            status=status.HTTP_200_OK
        )

    except Product.DoesNotExist:
        return Response(
            {'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        return Response(
            {'message': 'Error deleting product', 'data': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
