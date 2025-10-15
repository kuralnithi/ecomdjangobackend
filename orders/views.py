import razorpay
import hashlib
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
def create_order(request):
    print("Request Data:", request.data)
    try:
        cart_items = request.data
        amount = sum(item['product']['price'] * item['qty'] for item in cart_items)
        amount = round(amount, 2)
        
        order = Order.objects.create(
            cartItems=cart_items,
            amount=amount,
            status='pending'
        )
        
        serializer = OrderSerializer(order)
        return Response({
            'message': 'order created',
            'data': serializer.data
        })
        
    except Exception as e:
        return Response(
            {'message': 'error creating order', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def razor_payment(request):
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        options = request.data.copy()

        # Convert rupees to paise
        if 'amount' in options:
            options['amount'] = int(float(options['amount']) * 100)

        print("Payment Options (in paise):", options)

        order = client.order.create(options)
        if not order:
            return Response({'message': 'failed to create order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'order created successfully', 'data': order})
    except Exception as e:
        return Response({'message': 'failed to create order', 'data': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt  # ✅ Important: Disable CSRF since Razorpay posts directly
@api_view(['POST'])
def payment_validation(request):
    try:
        # 1️⃣ Get the data sent from frontend (paymentHandler)
        data = request.data
        print("🔹 Payment validation data received:", data)

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {"message": "Missing required payment fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2️⃣ Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # 3️⃣ Prepare parameters for signature verification
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        # 4️⃣ Verify signature (this will raise SignatureVerificationError if invalid)
        client.utility.verify_payment_signature(params_dict)

        # 5️⃣ If no exception → payment is valid
        return Response(
            {"message": "Payment verified successfully"},
            status=status.HTTP_200_OK,
        )

    except razorpay.errors.SignatureVerificationError:
        # Razorpay will throw this if the signature doesn't match
        return Response(
            {"message": "this transaction is not valid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        # Any other issue (e.g. key error, network)
        return Response(
            {"message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        # Create SHA256 hash
        generated_signature = hashlib.sha256(
            f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            return Response(
                {'message': 'this transaction is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({
            'message': 'this transaction is valid',
            'data': request.data
        })
        
    except Exception as e:
        return Response(
            {'message': 'error in payment validation', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )