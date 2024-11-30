from payment.models.transaction import Transaction
from django.db import transaction
from payment.client import MercadoPagoService
import logging

# Configurar o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreatePaymentUseCase:
    def execute(self, order):
        # Create a payment transaction
        try:
            with transaction.atomic():
                # Create a new Transaction object
                payment = Transaction(
                    order=order,
                    status='aguardando',  # You can set the initial status as 'pago' or any desired value
                    external_id='',  # You can set an external ID if needed
                )
                payment.save()
        except Exception as e:
            raise Exception('Failed to create payment transaction: {}'.format(str(e)))

        return payment
    
class CheckoutOrderUseCase:
    def execute(self, order, transaction_amount):

        transaction_amount

        try:
            # Integrate Mercado Pago QR Code generation
            mercado_pago_service = MercadoPagoService()
            print(transaction_amount)
            print(order)
            response_data = mercado_pago_service.create_qr_code(order, transaction_amount)
            qr_code = response_data.get("qr_data")
            in_store_order_id = response_data.get("in_store_order_id")
            
            logger.info(f'Successfully created QR code and in_store_order_id for order ID {order}: QR code={qr_code}, in_store_order_id={in_store_order_id}')

            # Save the QR code and in_store_order_id in the Payment model
            payment = Transaction.objects.create(
                order_id=order, 
                qrcode=qr_code, 
                external_id=in_store_order_id,  # Save the in_store_order_id in the external_id field
                amount=transaction_amount,
                status='generated'
            )
            logger.info(f'Payment record created with QR code and in_store_order_id for order ID {order}.')
            
            return payment  # Return the created payment
        except Exception as e:
            logger.error(f'Error during QR code generation or payment record creation for order ID {order}: {str(e)}')
            raise

        
# class CheckoutOrderUseCase:
#     def execute(self, order):
#         if order.status == 'em aberto':
#             # Call the CreatePaymentUseCase to create a payment transaction
#             create_payment_use_case = CreatePaymentUseCase()
#             create_payment_use_case.execute(order)

#             # Update the order status to 'recebido'
#             order.status = 'recebido'
#             order.save()
#         else:
#             raise Exception('Esse pedido não pode ser finalizado.')
