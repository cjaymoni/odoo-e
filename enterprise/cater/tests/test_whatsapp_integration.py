from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json


@tagged('cater', 'catering_whatsapp')
class TestWhatsAppIntegration(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Create test WhatsApp service
        self.whatsapp_service = self.env['cater.whatsapp.service'].create({
            'name': 'Test WhatsApp Service',
            'account_sid': 'test_account_sid',
            'auth_token': 'test_auth_token',
            'from_number': '+1234567890',
            'active': True,
        })
        
        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'mobile': '+233241234567',
            'is_catering_customer': True,
            'whatsapp_opt_in': True,
        })
        
        # Create test booking
        self.booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Test Wedding',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=30),
            'venue': 'Test Venue',
            'guest_count': 100,
            'state': 'completed'
        })

    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """Test successful WhatsApp message sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'sid': 'SM123456789',
            'status': 'queued',
            'num_segments': 1
        }
        mock_post.return_value = mock_response
        
        # Send message
        result = self.whatsapp_service.send_message(
            '+233241234567',
            'Test message'
        )
        
        # Assertions
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Check log creation
        log = self.env['cater.whatsapp.log'].search([
            ('to_number', '=', '+233241234567'),
            ('message', '=', 'Test message')
        ])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.status, 'queued')
        self.assertEqual(log.message_sid, 'SM123456789')

    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        """Test failed WhatsApp message sending"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'message': 'Invalid phone number'
        }
        mock_post.return_value = mock_response
        
        # Send message
        result = self.whatsapp_service.send_message(
            'invalid_number',
            'Test message'
        )
        
        # Assertions
        self.assertFalse(result)
        
        # Check error log
        log = self.env['cater.whatsapp.log'].search([
            ('to_number', '=', 'invalid_number'),
            ('status', '=', 'failed')
        ])
        self.assertEqual(len(log), 1)
        self.assertIn('Invalid phone number', log.error_message)

    @patch('requests.get')
    def test_connection_test_success(self, mock_get):
        """Test successful connection test"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test connection
        ok, message = self.whatsapp_service.test_connection()
        
        # Assertions
        self.assertTrue(ok)
        self.assertIn('verified', message)

    @patch('requests.get')
    def test_connection_test_failure(self, mock_get):
        """Test failed connection test"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Authentication failed'
        }
        mock_get.return_value = mock_response
        
        # Test connection
        ok, message = self.whatsapp_service.test_connection()
        
        # Assertions
        self.assertFalse(ok)
        self.assertIn('Authentication failed', message)

    @patch('requests.post')
    def test_send_template_message(self, mock_post):
        """Test sending template message"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'sid': 'SM987654321',
            'status': 'queued'
        }
        mock_post.return_value = mock_response
        
        # Send template message
        variables = {'customer_name': 'John Doe', 'event_date': '2025-10-15'}
        result = self.whatsapp_service.send_template(
            '+233241234567',
            'HX1234567890',
            variables
        )
        
        # Assertions
        self.assertTrue(result)
        
        # Check API call
        call_args = mock_post.call_args
        self.assertIn('ContentSid', call_args[1]['data'])
        self.assertIn('ContentVariables', call_args[1]['data'])

    def test_inactive_service(self):
        """Test that inactive service doesn't send messages"""
        # Deactivate service
        self.whatsapp_service.active = False
        
        # Try to send message
        result = self.whatsapp_service.send_message(
            '+233241234567',
            'Test message'
        )
        
        # Should return False
        self.assertFalse(result)

    @patch('requests.post')
    def test_feedback_request_automation(self, mock_post):
        """Test automated feedback request sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'sid': 'SM111222333', 'status': 'sent'}
        mock_post.return_value = mock_response
        
        # Trigger feedback request
        self.booking._send_feedback_request()
        
        # Check that message was sent
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('feedback', call_args[1]['data']['Body'].lower())
        self.assertIn('rating', call_args[1]['data']['Body'].lower())

    def test_opt_out_handling(self):
        """Test that opt-out customers don't receive messages"""
        # Opt out customer
        self.partner.whatsapp_opt_in = False
        
        # Try to send feedback request
        with patch('requests.post') as mock_post:
            self.booking._send_feedback_request()
            
            # Should not call API
            mock_post.assert_not_called()

    def test_missing_mobile_number(self):
        """Test handling of missing mobile number"""
        # Remove mobile number
        self.partner.mobile = False
        
        # Try to send message
        result = self.whatsapp_service.send_message(
            None,
            'Test message'
        )
        
        # Should return False
        self.assertFalse(result)

    @patch('requests.post')
    def test_network_error_handling(self, mock_post):
        """Test network error handling"""
        # Mock network error
        mock_post.side_effect = Exception('Network error')
        
        # Try to send message
        result = self.whatsapp_service.send_message(
            '+233241234567',
            'Test message'
        )
        
        # Should handle error gracefully
        self.assertFalse(result)
        
        # Check error log
        log = self.env['cater.whatsapp.log'].search([
            ('to_number', '=', '+233241234567'),
            ('status', '=', 'error')
        ])
        self.assertGreaterEqual(len(log), 1, "Should have at least one error log")
        error_logs = log.filtered(lambda l: 'Network error' in (l.error_message or ''))
        self.assertGreaterEqual(len(error_logs), 1, "Should have at least one network error log")
