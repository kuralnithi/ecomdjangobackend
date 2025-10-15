from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
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

@api_view(['POST'])
def add_products(request):
    try:
        name = request.data.get('name')
        
        # Upsert logic - update if exists, create if not
        product, created = Product.objects.update_or_create(
            name=name,
            defaults=request.data
        )
        
        serializer = ProductSerializer(product)
        message = 'product updated successfully' if not created else 'product added successfully'
        
        return Response({
            'message': message,
            'data': serializer.data
        })
        
    except Exception as e:
        return Response(
            {'message': 'error in adding product', 'data': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )