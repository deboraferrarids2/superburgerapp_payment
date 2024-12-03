import random
from unittest.mock import patch
from django.test import TestCase, Client
from rest_framework.test import APITestCase
from payment.models import Transaction
from payment.client import MercadoPagoService
from django.urls import reverse
import logging
from rest_framework import status

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class TestTransactionViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('create_and_retrieve_transaction')  # Ajuste o nome da URL para o seu caso
        # Gerando um ID único para cada teste
        self.transaction_data = {
            "transaction_amount": 1000,
            "order": str(random.randint(100000, 999999))  # Gera um número com 6 dígitos       
        }
        self.context = {} 

    def test_create_and_retrieve_transaction_post_success(self):
        """Teste para criação bem-sucedida da transação."""
        url = reverse('create_and_retrieve_transaction')
        logger.debug(f"Test POST started for URL: {url}")

        # Mocking MercadoPagoService's create_qr_code method
        with patch.object(MercadoPagoService, 'create_qr_code', return_value={
            'qr_data': 'sample_qr_code',
            'in_store_order_id': 'sample_order_id'
        }):

            # Mocking the save method of Transaction
            with patch.object(Transaction, 'save', return_value=None) as mock_save:
                logger.debug(f"Sending POST request with data: {self.transaction_data}")
                response = self.client.post(url, data=self.transaction_data, content_type='application/json')

                logger.debug(f"Response status code: {response.status_code}")
                self.assertEqual(response.status_code, 200)  

                response_data = response.json()
                logger.info(f"Response data: {response_data}")

                self.assertIn('transaction', response_data)
                self.assertEqual(response_data['transaction']['order_id'], self.transaction_data['order'])
                self.assertEqual(response_data['transaction']['status'], 'generated')
                self.assertEqual(response_data['transaction']['qrcode'], 'sample_qr_code')
                self.assertEqual(response_data['transaction']['external_id'], 'sample_order_id')

                self.context['external_id'] = response_data['transaction']['external_id']

                mock_save.assert_called_once()  # Ensure that save was called
    

    def test_create_transaction_invalid_json(self):
        """Testa se a view retorna erro quando o JSON enviado é inválido."""
        invalid_json = '{"transaction_amount": '', "order": {}}'  # JSON malformado
        response = self.client.post(self.url, invalid_json, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid JSON data')


    def test_create_transaction_missing_param(self):
        """Testa se a view retorna erro quando falta parâmetro obrigatório."""
        invalid_payload = '{"transaction_amount": ''}'
        response = self.client.post(self.url, invalid_payload, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid JSON data')
    
    @patch('payment.client.MercadoPagoService.create_qr_code')
    def test_error_create_qrcode(self, mock_create_qr_code):
        """Teste para falha ao criar o QR code da transação"""

        url = reverse('create_and_retrieve_transaction')  # Ajuste o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")

        # Simulando uma falha no método 'create_qr_code'
        mock_create_qr_code.side_effect = Exception("Erro ao criar QR Code")
        
        # Envia a solicitação POST com dados válidos de transação
        response = self.client.post(url, data=self.transaction_data, content_type='application/json')

        logger.debug(f"Response status code: {response.status_code}")
        
        # Verifica se a resposta foi de erro, pois houve falha ao criar o QR Code
        self.assertEqual(response.status_code, 400)  # Ou outro código adequado para erro interno

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém uma mensagem de erro adequada
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Erro ao criar QR Code')


    def test_create_transaction_missing_order(self):
        """Teste para verificar a validação de campos obrigatórios (order)."""
    
        # Remove o campo 'order' dos dados
        invalid_data = self.transaction_data.copy()
        del invalid_data['order']
        
        url = reverse('create_and_retrieve_transaction')
        response = self.client.post(url, data=invalid_data, content_type='application/json')

        self.assertEqual(response.status_code, 400)  # Verifica que houve um erro de validação
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Missing parameters: order')


from unittest.mock import patch
from django.test import TestCase, Client
from rest_framework.test import APITestCase
from rest_framework import status
import logging

# Seu logger
logger = logging.getLogger(__name__)

class TestTransactionWebhookViews(APITestCase):

    def setUp(self):
        self.client = Client()

        self.transaction = Transaction.objects.create(
            amount=1000,
            order_id=str(random.randint(100000, 999999)),
            status="generated",
            external_id="sample_order_id"
        )


    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_webhook_failure_due_to_invalid_data(self, mock_execute):
        """Teste para falha ao processar o webhook devido a dados inválidos"""
        
        # Simula um erro ao processar o webhook
        mock_execute.side_effect = Exception("Erro ao processar o webhook")

        # Payload inválido (sem dados necessários)
        invalid_payload = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "action": "payment.updated",
            "data": {}  # Faltando o 'id' dentro de 'data'
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")
        logger.debug(f"Sending POST request with data: {invalid_payload}")

        # Envia a solicitação POST com o payload inválido
        response = self.client.post(url, data=invalid_payload, content_type='application/json')

        # Verifica a resposta
        logger.debug(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém a mensagem de falha
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Invalid request')

    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_webhook_failure_due_to_missing_fields(self, mock_execute):
        """Teste para falha ao processar o webhook devido a campos faltando no payload"""

        # Simula que o execute foi chamado mas a execução falhou por dados inválidos
        mock_execute.return_value = False

        # Payload inválido (sem 'action' ou 'resource_id')
        invalid_payload = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            # "action": "payment.updated",  # 'action' está faltando
            "data": {
                # 'id' também está faltando dentro de 'data'
            }
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")
        logger.debug(f"Sending POST request with data: {invalid_payload}")

        # Envia a solicitação POST com o payload inválido
        response = self.client.post(url, data=invalid_payload, content_type='application/json')

        # Verifica a resposta
        logger.debug(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém a mensagem de falha
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Invalid request')

    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_missing_action_or_resource_id(self, mock_execute):
        """Teste para falha ao processar o webhook devido a campos faltando no payload"""

        # Simula que o execute foi chamado mas a execução falhou por dados inválidos
        mock_execute.return_value = False

        # Payload inválido (sem 'action' ou 'resource_id')
        invalid_payload = {
            "data": {"id": "sample_order_id"}
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")
        logger.debug(f"Sending POST request with data: {invalid_payload}")

        # Envia a solicitação POST com o payload inválido
        response = self.client.post(url, data=invalid_payload, content_type='application/json')

        # Verifica a resposta
        logger.debug(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém a mensagem de falha
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Invalid request')

    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_failed_webhook_processing(self, mock_execute):
        """Teste para falha ao processar o webhook devido a campos faltando no payload"""

        # Simula que o execute foi chamado mas a execução falhou por dados inválidos
        mock_execute.return_value = False

        # Payload inválido (sem 'action' ou 'resource_id')
        invalid_payload = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "date_created": "2015-03-25T10:04:58.396-04:00",
            "user_id": 407707350,
            "api_version": "v1",
            "action": "payment.updated",
            "data": {
                "id": "452b061b-07e2-4c00-80b7-08477bf58bf8"
            }
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")
        logger.debug(f"Sending POST request with data: {invalid_payload}")

        # Envia a solicitação POST com o payload inválido
        response = self.client.post(url, data=invalid_payload, content_type='application/json')

        # Verifica a resposta
        logger.debug(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém a mensagem de falha
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Webhook processing failed')


    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_exception_in_webhook_processing(self, mock_execute):
        """Teste para falha ao processar o webhook devido a campos faltando no payload"""

        # Simula que o execute foi chamado mas a execução falhou por dados inválidos
        mock_execute.return_value = False

        # Payload inválido (sem 'action' ou 'resource_id')
        invalid_payload = {
            "action": "payment.created",
            "data": {"id": "sample_order_id"}
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")
        logger.debug(f"Sending POST request with data: {invalid_payload}")

        # Envia a solicitação POST com o payload inválido
        response = self.client.post(url, data=invalid_payload, content_type='application/json')

        # Verifica a resposta
        logger.debug(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém a mensagem de falha
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Webhook processing failed')


    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_webhook_success(self, mock_execute):
        """Teste para sucesso ao processar o webhook"""

        # Simula uma resposta de sucesso para o processamento do webhook
        mock_execute.return_value = True
        
        # Payload válido com o ID da transação
        valid_payload = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "action": "payment.updated",
            "data": {
                "id": 'sample_order_id'
            }
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        # Envia a solicitação POST com o payload válido
        response = self.client.post(url, data=valid_payload, content_type='application/json')
        # Verifica a resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        logger.info(f'resopnse: {response_data}')

        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Webhook processed successfully')

    
    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_usecases_unknown_action(self, mock_execute):
        """Teste para falha ao processar o webhook devido a campos faltando no payload"""

        # Simula que o execute foi chamado mas a execução falhou por dados inválidos
        mock_execute.return_value = False

        # Payload inválido (sem 'action' ou 'resource_id')
        invalid_payload = {
            "action": "payment.altered",
            "data": {"id": "sample_order_id"}
        }

        url = reverse('mercado_pago_webhook')  # Ajuste para o nome da sua URL
        logger.debug(f"Test POST started for URL: {url}")
        logger.debug(f"Sending POST request with data: {invalid_payload}")

        # Envia a solicitação POST com o payload inválido
        response = self.client.post(url, data=invalid_payload, content_type='application/json')

        # Verifica a resposta
        logger.debug(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        logger.info(f"Response data: {response_data}")

        # Verifica se a resposta contém a mensagem de falha
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Webhook processing failed')


from django.test import TestCase
from .models import Transaction
from django.utils import timezone

class TransactionModelTest(TestCase):
    
    def setUp(self):
        """
        Esse método é chamado antes de cada teste. 
        Aqui, podemos criar dados de teste.
        """
        self.transaction_data = {
            'order_id': 'ORD123456',
            'status': 'pending',
            'amount': 1000,
            'external_id': 'EXT123456',
            'qrcode': 'QR123456',
            'date_created': timezone.now(),
            'last_updated': timezone.now(),
        }
        # Criando uma instância do modelo Transaction
        self.transaction = Transaction.objects.create(**self.transaction_data)

    def test_transaction_creation(self):
        """Testa se a transação foi criada corretamente."""
        transaction = self.transaction
        self.assertEqual(transaction.order_id, self.transaction_data['order_id'])
        self.assertEqual(transaction.status, self.transaction_data['status'])
        self.assertEqual(transaction.amount, self.transaction_data['amount'])
        self.assertEqual(transaction.external_id, self.transaction_data['external_id'])
        self.assertEqual(transaction.qrcode, self.transaction_data['qrcode'])
        self.assertIsNotNone(transaction.date_created)
        self.assertIsNotNone(transaction.last_updated)
        
    def test_transaction_str_method(self):
        """Testa se o método __str__ do modelo retorna o valor esperado."""
        transaction = self.transaction
        expected_str = f'Transaction for Order ID: {self.transaction_data["order_id"]}'
        self.assertEqual(str(transaction), expected_str)
    
    def test_transaction_amount_is_positive(self):
        """Testa se o campo amount sempre será positivo."""
        transaction = self.transaction
        self.assertGreater(transaction.amount, 0)

    def test_transaction_external_id_can_be_null(self):
        """Testa se o campo external_id pode ser nulo."""
        transaction = Transaction.objects.create(
            order_id='ORD654321',
            status='completed',
            amount=500,
            external_id=None,  # Deixando o campo external_id como None
            qrcode='QR654321',
            date_created=timezone.now(),
            last_updated=timezone.now(),
        )
        self.assertIsNone(transaction.external_id)
