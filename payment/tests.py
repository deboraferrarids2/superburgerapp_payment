# -*- coding: utf-8 -*-

from unittest.mock import patch
from django.test import TestCase, Client
from payment.models import Transaction
from payment.client import MercadoPagoService
from django.urls import reverse
import logging

# Configuração do logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Definindo o nível de log como DEBUG

class TestTransactionViews(TestCase):

    def setUp(self):
        # Método de setup para os testes, equivalente ao pytest.fixture
        self.client = Client()
        self.transaction_data = {
            "transaction_amount": 100.0,
            "order": "12345"
        }

    def test_create_and_retrieve_transaction_post(self):
        url = reverse('create_and_retrieve_transaction')
        logger.debug(f"Test POST started for URL: {url}")

        # Mocking MercadoPagoService's create_qr_code method
        with patch.object(MercadoPagoService, 'create_qr_code', return_value={
            'qr_data': 'sample_qr_code',
            'in_store_order_id': 'sample_order_id'
        }):
            # Mocking Transaction's save method to avoid saving in the DB
            with patch.object(Transaction, 'save', lambda x: None):
                logger.debug(f"Sending POST request with data: {self.transaction_data}")
                response = self.client.post(url, data=self.transaction_data, content_type='application/json')

                logger.debug(f"Response status code: {response.status_code}")
                self.assertEqual(response.status_code, 201)

                response_data = response.json()
                logger.debug(f"Response data: {response_data}")

                self.assertIn('transaction', response_data)
                self.assertEqual(response_data['transaction']['order_id'], self.transaction_data['order'])
                self.assertEqual(response_data['transaction']['status'], 'approved')
                self.assertEqual(response_data['transaction']['qr_code'], 'sample_qr_code')
                self.assertEqual(response_data['transaction']['external_id'], 'sample_order_id')

                # Verify that no actual Transaction object was created
                # No Transaction object is created in the DB, so this will raise an exception if not mocked correctly
                with self.assertRaises(Transaction.DoesNotExist):
                    Transaction.objects.get(order=self.transaction_data['order'])

    def test_create_and_retrieve_transaction_get(self):
        # Mocking the retrieval of a transaction object
        with patch.object(Transaction.objects, 'get', return_value=Transaction(order='12345', status='approved', amount=100.0)):
            url = reverse('create_and_retrieve_transaction') + '?order_id=12345'
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(response_data['order_id'], '12345')
            self.assertEqual(response_data['status'], 'approved')
            self.assertEqual(response_data['amount'], 100.0)
