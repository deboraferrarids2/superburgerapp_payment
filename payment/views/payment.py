from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from payment.models.transaction import Transaction
from payment.client import MercadoPagoClient
from django.utils import timezone
import json

@csrf_exempt
def create_and_retrieve_transaction(request):
    if request.method == 'POST':
        print(request.body.decode('utf-8'))  # Print the raw JSON data

        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Extract required parameters from json_data
        required_params = ['transaction_amount', 'payer_email']

        missing_params = [param for param in required_params if param not in json_data]
        if missing_params:
            return JsonResponse({'error': f'Missing parameters: {", ".join(missing_params)}'}, status=400)

        # Validate parameters if needed
        # ...

        # Process payment using MercadoPagoClient
        client = MercadoPagoClient("ENV_ACCESS_TOKEN")
        try:
            payment_response = client.process_payment(
                json_data['transaction_amount'],
                json_data['payer_email'],
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


        # Extract relevant information from the payment response
        order_id = json_data['order_id']
        status = payment_response.get('status')
        amount = payment_response.get('transaction_amount')  # Assuming 'transaction_amount' is the correct field

        # Extracting additional information for date_created and last_updated
        date_created_str = payment_response.get('date_created')
        date_updated_str = payment_response.get('date_last_updated')

        # Convert date strings to datetime objects
        date_created = timezone.datetime.fromisoformat(date_created_str)
        date_updated = timezone.datetime.fromisoformat(date_updated_str)

        # Extract QR code information
        qrcode = payment_response.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code')

        # Create a new Transaction object
        transaction = Transaction.objects.create(
            order_id=order_id,
            status=status,
            amount=amount,
            date_created=date_created,
            last_updated=date_updated,
            qrcode=qrcode,
            # Set other fields as needed
        )
        

        # Return the created transaction as JSON response
        response_data = {
            'message': 'Transaction created successfully',
            'transaction': {
                'order_id': transaction.order_id,
                'status': transaction.status,
                'amount': str(transaction.amount),
                'date_created': transaction.date_created.isoformat(),
                'last_updated': transaction.last_updated.isoformat(),
                'qrcode': transaction.qrcode,
                # Include other fields as needed
            }
        }
        return JsonResponse(response_data, status=201)

    # ... (rest of the view remains the same)



    elif request.method == 'GET':
        # Retrieve and return the current transaction data for a specific order
        order_id_to_retrieve = request.GET.get('order_id')
        try:
            transaction = Transaction.objects.get(order_id=order_id_to_retrieve)
            transaction_data = {
                'order_id': transaction.order_id,
                'status': transaction.status,
                'amount': str(transaction.amount),
                # Include other fields as needed
            }
            return JsonResponse(transaction_data)
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found'}, status=404)

@csrf_exempt  # Disable CSRF protection for webhook endpoint
@require_POST
def mercado_pago_webhook(request):
    # Process Mercado Pago webhook notification and update Transaction model
    # ...

    # For demonstration purposes, let's assume you get data from Mercado Pago webhook
    order_id = '12345'
    new_status = 'paid'

    try:
        transaction = Transaction.objects.get(order_id=order_id)
        transaction.status = new_status
        # Update or add other fields as needed
        transaction.save()

        # Call another microservice endpoint as a POST method
        # ...

        return JsonResponse({'message': 'Webhook processed successfully'})
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
