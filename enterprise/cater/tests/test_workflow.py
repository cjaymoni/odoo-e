from odoo.addons.base.tests.common import SavepointCaseWithUserDemo as SavepointCase
from odoo.tests.common import tagged
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


@tagged('cater', 'workflow', 'post_install', '-at_install')
class TestBookingWorkflow(SavepointCase):
    """Test booking state transitions and workflow using SavepointCase for transaction isolation"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test data
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'mobile': '+233241234567',
            'email': 'test@customer.com',
            'is_catering_customer': True,
        })
        
        cls.category = cls.env['cater.menu.category'].create({
            'name': 'Main Dishes',
            'description': 'Traditional Ghanaian main dishes'
        })
        
        cls.menu_item = cls.env['cater.menu.item'].create({
            'name': 'Jollof Rice with Chicken',
            'category_id': cls.category.id,
            'price_per_person': 25.0,
            'minimum_order': 10,
        })
        
        cls.service = cls.env['cater.service'].create({
            'name': 'Additional Waiter',
            'service_type': 'staff',
            'price': 150.0,
        })

    def test_booking_draft_to_confirmed(self):
        """Test booking transition from draft to confirmed"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Wedding Reception',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=30),
            'venue': 'Accra International Conference Centre',
            'guest_count': 100,
        })
        
        # Add menu items
        self.env['cater.booking.menu.line'].create({
            'booking_id': booking.id,
            'menu_item_id': self.menu_item.id,
            'quantity': 100,
        })
        
        self.assertEqual(booking.state, 'draft')
        
        # Confirm booking
        booking.action_confirm()
        self.assertEqual(booking.state, 'confirmed')
        
    def test_booking_confirmed_to_in_progress(self):
        """Test booking transition from confirmed to in progress"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Corporate Event',
            'event_type': 'corporate',
            'event_date': datetime.now() + timedelta(days=15),
            'venue': 'Movenpick Ambassador Hotel',
            'guest_count': 75,
        })
        
        booking.write({'state': 'confirmed'})
        
        # Start event
        booking.action_start_event()
        self.assertEqual(booking.state, 'in_progress')
        
    def test_booking_in_progress_to_completed(self):
        """Test booking transition from in progress to completed"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Birthday Party',
            'event_type': 'birthday',
            'event_date': datetime.now() + timedelta(days=10),
            'venue': 'Private Residence',
            'guest_count': 30,
        })
        
        booking.write({'state': 'in_progress'})
        
        # Complete event
        booking.action_complete()
        self.assertEqual(booking.state, 'completed')
        
    def test_booking_cancellation(self):
        """Test booking cancellation from any state"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Cancelled Event',
            'event_type': 'other',
            'event_date': datetime.now() + timedelta(days=45),
            'venue': 'TBD',
            'guest_count': 50,
        })
        
        # Cancel from draft
        booking.action_cancel()
        self.assertEqual(booking.state, 'cancelled')
        
    def test_cannot_confirm_without_menu(self):
        """Test that booking cannot be confirmed without menu items"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Empty Menu Event',
            'event_type': 'graduation',
            'event_date': datetime.now() + timedelta(days=20),
            'venue': 'University Campus',
            'guest_count': 200,
        })
        
        # Attempt to confirm without menu items should fail
        with self.assertRaises(ValidationError):
            booking.action_confirm()


@tagged('cater', 'computed_fields', 'post_install', '-at_install')
class TestComputedFields(SavepointCase):
    """Test computed fields and dependencies"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'mobile': '+233241234567',
            'is_catering_customer': True,
        })
        
        cls.menu_item = cls.env['cater.menu.item'].create({
            'name': 'Test Menu Item',
            'category_id': cls.env['cater.menu.category'].create({'name': 'Test Category'}).id,
            'price_per_person': 20.0,
            'minimum_order': 5,
        })
        
        cls.service = cls.env['cater.service'].create({
            'name': 'Test Service',
            'service_type': 'equipment',
            'price': 100.0,
        })

    def test_menu_total_computation(self):
        """Test menu total is computed correctly"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Test Event',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=30),
            'venue': 'Test Venue',
            'guest_count': 50,
        })
        
        # Add menu items
        self.env['cater.booking.menu.line'].create({
            'booking_id': booking.id,
            'menu_item_id': self.menu_item.id,
            'quantity': 50,
        })
        
        expected_total = 50 * 20.0
        self.assertEqual(booking.menu_total, expected_total)
        
    def test_service_total_computation(self):
        """Test service total is computed correctly"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Test Event',
            'event_type': 'corporate',
            'event_date': datetime.now() + timedelta(days=25),
            'venue': 'Test Venue',
            'guest_count': 30,
        })
        
        # Add services
        self.env['cater.booking.service.line'].create({
            'booking_id': booking.id,
            'service_id': self.service.id,
            'quantity': 3,
        })
        
        expected_total = 3 * 100.0
        self.assertEqual(booking.service_total, expected_total)
        
    def test_total_amount_with_tax(self):
        """Test total amount includes VAT correctly"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Test Event',
            'event_type': 'birthday',
            'event_date': datetime.now() + timedelta(days=20),
            'venue': 'Test Venue',
            'guest_count': 40,
        })
        
        # Add menu items and services
        self.env['cater.booking.menu.line'].create({
            'booking_id': booking.id,
            'menu_item_id': self.menu_item.id,
            'quantity': 40,
        })
        
        self.env['cater.booking.service.line'].create({
            'booking_id': booking.id,
            'service_id': self.service.id,
            'quantity': 2,
        })
        
        expected_subtotal = (40 * 20.0) + (2 * 100.0)  # 800 + 200 = 1000
        expected_tax = expected_subtotal * 0.15  # 150
        expected_total = expected_subtotal + expected_tax  # 1150
        
        self.assertEqual(booking.subtotal, expected_subtotal)
        self.assertEqual(booking.tax_amount, expected_tax)
        self.assertEqual(booking.total_amount, expected_total)
        
    def test_booking_count_on_partner(self):
        """Test booking count is computed on partner"""
        # Create multiple bookings
        for i in range(3):
            self.env['cater.event.booking'].create({
                'partner_id': self.partner.id,
                'event_name': f'Event {i}',
                'event_type': 'other',
                'event_date': datetime.now() + timedelta(days=10 + i),
                'venue': 'Test Venue',
                'guest_count': 20,
            })
        
        # Check computed field
        self.assertEqual(self.partner.catering_booking_count, 3)


@tagged('cater', 'integration', 'post_install', '-at_install')
class TestIntegration(SavepointCase):
    """Test integration between models and complex scenarios"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.partner = cls.env['res.partner'].create({
            'name': 'Integration Test Customer',
            'mobile': '+233241234567',
            'email': 'integration@test.com',
            'is_catering_customer': True,
        })
        
        cls.menu_items = cls.env['cater.menu.item'].create([
            {
                'name': 'Jollof Rice',
                'category_id': cls.env['cater.menu.category'].create({'name': 'Main'}).id,
                'price_per_person': 25.0,
                'minimum_order': 10,
            },
            {
                'name': 'Fried Chicken',
                'category_id': cls.env['cater.menu.category'].create({'name': 'Protein'}).id,
                'price_per_person': 15.0,
                'minimum_order': 10,
            }
        ])
        
        cls.services = cls.env['cater.service'].create([
            {
                'name': 'Waiter',
                'service_type': 'staff',
                'price': 150.0,
            },
            {
                'name': 'Sound System',
                'service_type': 'equipment',
                'price': 500.0,
            }
        ])

    def test_full_booking_lifecycle(self):
        """Test complete booking lifecycle from creation to completion"""
        # Create booking
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'Complete Lifecycle Event',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=60),
            'venue': 'Labadi Beach Hotel',
            'guest_count': 150,
        })
        
        # Add menu items
        for menu_item in self.menu_items:
            self.env['cater.booking.menu.line'].create({
                'booking_id': booking.id,
                'menu_item_id': menu_item.id,
                'quantity': 150,
            })
        
        # Add services
        for service in self.services:
            self.env['cater.booking.service.line'].create({
                'booking_id': booking.id,
                'service_id': service.id,
                'quantity': 1,
            })
        
        # Confirm booking
        booking.action_confirm()
        self.assertEqual(booking.state, 'confirmed')
        
        # Start event
        booking.action_start_event()
        self.assertEqual(booking.state, 'in_progress')
        
        # Complete event
        booking.action_complete()
        self.assertEqual(booking.state, 'completed')
        
        # Create feedback
        feedback = self.env['cater.feedback'].create({
            'booking_id': booking.id,
            'rating': '5',
            'food_quality': 5,
            'service_quality': 5,
            'presentation': 5,
            'timeliness': 5,
            'comments': 'Excellent service!',
            'would_recommend': True,
        })
        
        self.assertEqual(feedback.partner_id, self.partner)
        
    def test_multiple_bookings_same_customer(self):
        """Test multiple bookings for the same customer"""
        bookings = []
        for i in range(5):
            booking = self.env['cater.event.booking'].create({
                'partner_id': self.partner.id,
                'event_name': f'Event {i+1}',
                'event_type': 'other',
                'event_date': datetime.now() + timedelta(days=10 * (i+1)),
                'venue': f'Venue {i+1}',
                'guest_count': 50 + (i * 10),
            })
            bookings.append(booking)
        
        # Check partner's booking count
        self.assertEqual(self.partner.catering_booking_count, 5)
        
        # Check bookings are linked
        partner_bookings = self.env['cater.event.booking'].search([
            ('partner_id', '=', self.partner.id)
        ])
        self.assertEqual(len(partner_bookings), 5)
