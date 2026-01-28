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
    def test_feedback_matching_with_explicit_reference(self, mock_post):
        """Test matching feedback using explicit booking reference"""
        # Ensure booking is set up for feedback
        self.booking.write({
            'state': 'completed',
            'feedback_request_sent': True,
            'feedback_request_date': datetime.now() - timedelta(minutes=10)
        })
        
        # Simulate incoming message with reference
        message = f"{self.booking.name} - 5 stars!"
        result = self.env['cater.event.booking']._process_whatsapp_feedback_response(
            self.partner.mobile, message
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(result.booking_id.id, self.booking.id)
        self.assertEqual(result.rating, '5')

    @patch('requests.post')
    def test_feedback_matching_shared_mobile(self, mock_post):
        """Test matching feedback when multiple partners share a mobile number"""
        # Create second partner with same mobile
        partner2 = self.env['res.partner'].create({
            'name': 'Partner 2',
            'mobile': self.partner.mobile,
            'is_catering_customer': True,
            'whatsapp_opt_in': True,
        })
        
        # Create booking for partner2
        booking2 = self.env['cater.event.booking'].create({
            'partner_id': partner2.id,
            'event_name': 'Event 2',
            'event_type': 'corporate',
            'event_date': datetime.now() + timedelta(days=5),
            'venue': 'Venue 2',
            'guest_count': 50,
            'state': 'completed',
            'feedback_request_sent': True,
            'feedback_request_date': datetime.now()
        })
        
        # Setup first booking (older request)
        self.booking.write({
            'state': 'completed',
            'feedback_request_sent': True,
            'feedback_request_date': datetime.now() - timedelta(hours=1)
        })
        
        # Simulate incoming message (no reference)
        # Should match booking2 because it's the more recent request
        result = self.env['cater.event.booking']._process_whatsapp_feedback_response(
            self.partner.mobile, "5 - Excellent service!"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(result.booking_id.id, booking2.id)
        self.assertEqual(result.partner_id.id, partner2.id)

    @patch('requests.post')
    def test_feedback_matching_recency(self, mock_post):
        """Test matching most recent request for same partner"""
        # Create second booking for same partner
        booking2 = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Event 2',
            'event_type': 'corporate',
            'event_date': datetime.now() + timedelta(days=5),
            'venue': 'Venue 2',
            'guest_count': 50,
            'state': 'completed',
            'feedback_request_sent': True,
            'feedback_request_date': datetime.now()
        })
        
        # Setup first booking (older request)
        self.booking.write({
            'state': 'completed',
            'feedback_request_sent': True,
            'feedback_request_date': datetime.now() - timedelta(hours=2)
        })
        
        # Simulate incoming message (no reference)
        result = self.env['cater.event.booking']._process_whatsapp_feedback_response(
            self.partner.mobile, "4 - Good"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(result.booking_id.id, booking2.id)
    @patch('requests.post')
    def test_feedback_matching_structured_detailed(self, mock_post):
        """Test matching and parsing structured detailed feedback with user's specific format"""
        # Ensure booking is set up for feedback
        self.booking.write({
            'state': 'completed',
            'feedback_request_sent': True,
            'feedback_request_date': datetime.now() - timedelta(minutes=5)
        })
        
        # Simulate structured message exactly as user suggested (with mixed spacing and indentation)
        message = f"""booking id: {self.booking.name}
                     Food Quality (1-5) : 5
                    Service (1-5) :4
                    Presentation (1-5):3
                    Timeliness (1-5):2
                    Comments: Everything was mostly fine."""
        
        result = self.env['cater.event.booking']._process_whatsapp_feedback_response(
            self.partner.mobile, message
        )
        
        # Assertions
        self.assertTrue(result, "Should successfully process the structured feedback")
        self.assertEqual(result.booking_id.id, self.booking.id)
        self.assertEqual(result.food_quality, 5)
        self.assertEqual(result.service_quality, 4)
        self.assertEqual(result.presentation, 3)
        self.assertEqual(result.timeliness, 2)
        self.assertEqual(result.comments, "Everything was mostly fine.")
        # Overall rating should be average: (5+4+3+2)/4 = 14/4 = 3.5 -> 4
        self.assertEqual(result.rating, '4')
