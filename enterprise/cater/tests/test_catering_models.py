from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

@tagged('cater', 'catering_models')
class TestCateringModels(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Create test data
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'mobile': '+233241234567',
            'is_catering_customer': True,
        })
        
        self.category = self.env['cater.menu.category'].create({
            'name': 'Main Dishes',
            'description': 'Traditional Ghanaian main dishes'
        })
        
        self.menu_item = self.env['cater.menu.item'].create({
            'name': 'Jollof Rice with Chicken',
            'category_id': self.category.id,
            'price_per_person': 25.0,
            'minimum_order': 10,
        })
        
        self.service = self.env['cater.service'].create({
            'name': 'Additional Waiter',
            'service_type': 'staff',
            'price': 150.0,
        })

    def test_booking_creation(self):
        """Test creating a new booking"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Wedding Reception',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=30),
            'venue': 'Accra International Conference Centre',
            'guest_count': 100,
        })
        
        self.assertEqual(booking.state, 'draft')
        # Check that a name was assigned (either from sequence or 'New' fallback)
        self.assertIsNotNone(booking.name)
        self.assertTrue(len(booking.name) > 0)
        
    def test_menu_line_calculation(self):
        """Test menu line subtotal calculation"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Test Event',
            'event_type': 'birthday',
            'event_date': datetime.now() + timedelta(days=15),
            'venue': 'Test Venue',
            'guest_count': 50,
        })
        
        menu_line = self.env['cater.booking.menu.line'].create({
            'booking_id': booking.id,
            'menu_item_id': self.menu_item.id,
            'quantity': 50,
        })
        
        expected_subtotal = 50 * 25.0  # quantity * price_per_person
        self.assertEqual(menu_line.subtotal, expected_subtotal)
        
    def test_booking_totals(self):
        """Test booking total calculations including VAT"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Corporate Event',
            'event_type': 'corporate',
            'event_date': datetime.now() + timedelta(days=20),
            'venue': 'Movenpick Ambassador Hotel',
            'guest_count': 75,
        })
        
        # Add menu item
        self.env['cater.booking.menu.line'].create({
            'booking_id': booking.id,
            'menu_item_id': self.menu_item.id,
            'quantity': 75,
        })
        
        # Add service
        self.env['cater.booking.service.line'].create({
            'booking_id': booking.id,
            'service_id': self.service.id,
            'quantity': 2,
        })
        
        expected_menu_total = 75 * 25.0  # 1875
        expected_service_total = 2 * 150.0  # 300
        expected_subtotal = expected_menu_total + expected_service_total  # 2175
        expected_tax = expected_subtotal * 0.15  # 326.25
        expected_total = expected_subtotal + expected_tax  # 2501.25
        
        self.assertEqual(booking.menu_total, expected_menu_total)
        self.assertEqual(booking.service_total, expected_service_total)
        self.assertEqual(booking.subtotal, expected_subtotal)
        self.assertEqual(booking.tax_amount, expected_tax)
        self.assertEqual(booking.total_amount, expected_total)
        
    def test_minimum_order_validation(self):
        """Test minimum order quantity validation"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Small Event',
            'event_type': 'birthday',
            'event_date': datetime.now() + timedelta(days=10),
            'venue': 'Home',
            'guest_count': 5,
        })
        
        with self.assertRaises(ValidationError):
            self.env['cater.booking.menu.line'].create({
                'booking_id': booking.id,
                'menu_item_id': self.menu_item.id,
                'quantity': 5,  # Less than minimum order of 10
            })
            
    def test_event_date_validation(self):
        """Test that event date must be in future"""
        with self.assertRaises(ValidationError):
            self.env['cater.event.booking'].create({
                'partner_id': self.partner.id,
                'event_name': 'Past Event',
                'event_type': 'other',
                'event_date': datetime.now() - timedelta(days=1),
                'venue': 'Test Venue',
                'guest_count': 20,
            })
            
    def test_feedback_creation(self):
        """Test feedback creation"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Test Event',
            'event_type': 'graduation',
            'event_date': datetime.now() - timedelta(days=5),  # Past date for completed event
            'venue': 'University of Ghana',
            'guest_count': 200,
            'state': 'completed'
        })
        
        feedback = self.env['cater.feedback'].create({
            'booking_id': booking.id,
            'rating': '5',
            'comments': 'Excellent service and delicious food!',
            'food_quality': 5,
            'service_quality': 5,
        })
        
        self.assertEqual(feedback.partner_id, self.partner)
        self.assertEqual(feedback.rating, '5')
