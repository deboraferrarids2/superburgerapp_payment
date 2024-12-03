from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from payment.models.transaction import Transaction
from payment.client import MercadoPagoService
from django.utils import timezone
import json

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from payment.use_cases.payment import CheckoutOrderUseCase
from payment.models.transaction import Transaction
from payment.serializers.transactions import TransactionSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import json
from payment.client import MercadoPagoService
from payment.models.transaction import Transaction
from payment.use_cases.payment import CheckoutOrderUseCase

@api_view(['POST'])
@csrf_exempt
def create_and_retrieve_transaction(request):
    if request.method == 'POST':
        print(request.body.decode('utf-8'))  # Print the raw JSON data

        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract required parameters from json_data
        required_params = ['transaction_amount', 'order']
        missing_params = [param for param in required_params if param not in json_data]

        if missing_params:
            return Response({'error': f'Missing parameters: {", ".join(missing_params)}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = json_data['order']
            transaction_amount = json_data['transaction_amount']
            
            # Use CheckoutOrderUseCase to handle the payment creation
            use_case = CheckoutOrderUseCase()
            payment = use_case.execute(order, transaction_amount)

            # Serialize the payment data
            serializer = TransactionSerializer(payment)
            return Response({
                'message': 'Order status updated to "processando".',
                'transaction': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
@action(detail=True, methods=['get'], url_path='status', permission_classes=[AllowAny])
def get_transactions_for_order(self, request, pk=None):
    order = self.get_object()
    transactions = Transaction.objects.filter(order=order)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
