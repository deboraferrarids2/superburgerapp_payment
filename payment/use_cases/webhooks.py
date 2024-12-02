import http.client
import json
import requests
from django.conf import settings
from payment.models.transaction import Transaction
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ProcessWebhookUseCase:
    def execute(self, action, resource_id):
        url = None
        if action == 'payment.updated':
            url = f'/v1/payments/{resource_id}'
        elif action == 'chargebacks':
            url = f'/v1/chargebacks/{resource_id}'
        elif action == 'merchant_order':
            url = f'/merchant_orders/{resource_id}'
        else:
            logger.error(f'Unknown action: {action}')
            return False
        
        headers = {
            'Authorization': f'Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}'
        }

        try:
            # Create a connection to the API server
            connection = http.client.HTTPSConnection("api.mercadopago.com")

            # Make the GET request
            connection.request("GET", url, headers=headers)
            response = connection.getresponse()
            response_data = response.read().decode()

            logger.info(f'API response status: {response.status}')
            logger.info(f'API response data: {response_data}')

            if response.status != 200:
                logger.error(f'Failed API request with status {response.status}: {response_data}')
                pass
                #return False
            else:
                # Parse the JSON response
                data = json.loads(response_data)
                return self.process_data(action, data)
            
            try:
                logger.info(f'Updating status')
                # Find the payment record by external_id
                transaction = Transaction.objects.get(external_id=resource_id)
                logger.info(f'Updating status para transaction: {transaction}')
                # Update the payment status to "approved"
                transaction.status = 'approved'
                transaction.save()

                # # Update the associated order status to "Recebido"
                # order = transaction.order
                # logger.info(f'Updating status para order: {order}')
                # order.status = 'recebido'
                # order.save()
                # logger.info(f'Updated order to recebido')
                # return True  # Indicate that the error handling succeeded
                self.update_order_status(transaction)
                return True  # Success
            except Transaction.DoesNotExist:
                logger.error(f'Payment with external_id {resource_id} does not exist')
                return False
        
        # except Exception as e:
        #     logger.error(f'Exception during API request or processing: {e}')
        except:
            pass


    def process_data(self, topic, data):
        logger.info(f'Processing data for topic: {topic}')
        if topic == 'payment':
            return self.process_payment(data)
        logger.error(f'Unknown topic: {topic}')
        return False

    def process_payment(self, data):
        transaction_id = data.get('id')
        transaction_status = data.get('status')

        logger.info(f'Processing payment with ID: {transaction_id} and status: {transaction_status}')

        if transaction_id and transaction_status:
            try:
                # Search transaction
                transaction = Transaction.objects.get(external_id=transaction_id)

                # Update transaction status
                transaction.status = transaction_status
                transaction.save()

                # if transaction_status == 'approved':
                #     order = transaction.order
                #     order.status = 'Recebido'
                #     order.save()

                # Update the order status in order-app
                print(f'001')
                self.update_order_status(transaction)
                return True  # Success
            except Transaction.DoesNotExist:
                logger.error(f'Transaction with ID {transaction_id} does not exist')
                return False
        return False

    def update_order_status(self, transaction):
        """Update the order status in order-app."""
        try:
            print(f'002')
            order_id=transaction.order_id
            url = f"http://order-app:5000/order/{order_id}/status/"
            payload = {"status": 'recebido'}
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            logger.info(f'Successfully updated order {order_id} status to recebido')
        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to update order {order_id} status: {e}')

