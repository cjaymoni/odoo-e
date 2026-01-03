from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta


@tagged('cater', 'catering_security')
class TestSecurityAccess(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Create test groups
        self.staff_group = self.env.ref('cater.catering_staff_group')  # Event Planner
        self.manager_group = self.env.ref('cater.catering_manager_group')  # Admin
        self.accountant_group = self.env.ref('cater.catering_accountant_group')  # Accountant
        self.client_group = self.env.ref('cater.catering_client_group')  # Client
        
        # Create test users
        self.staff_user = self.env['res.users'].create({
            'name': 'Event Planner User',
            'login': 'eventplanner@test.com',
            'groups_id': [(6, 0, [self.staff_group.id])]
        })
        
        self.manager_user = self.env['res.users'].create({
            'name': 'Admin User',
            'login': 'admin@test.com',
            'groups_id': [(6, 0, [self.manager_group.id])]
        })
        
        self.accountant_user = self.env['res.users'].create({
            'name': 'Accountant User',
            'login': 'accountant@test.com',
            'groups_id': [(6, 0, [self.accountant_group.id])]
        })
        
        self.client_user = self.env['res.users'].create({
            'name': 'Client User',
            'login': 'client@test.com',
            'groups_id': [(6, 0, [self.client_group.id])]
        })
        
        # Create test partners
        self.client_partner = self.env['res.partner'].create({
            'name': 'Client Partner',
            'is_catering_customer': True,
            'user_ids': [(4, self.client_user.id)]
        })
        
        self.other_client_partner = self.env['res.partner'].create({
            'name': 'Other Client Partner',
            'is_catering_customer': True
        })
        
        # Create test bookings
        self.client_booking = self.env['cater.event.booking'].create({
            'partner_id': self.client_partner.id,
            'event_name': 'Client Event',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=30),
            'venue': 'Client Venue',
            'guest_count': 50
        })
        
        self.other_booking = self.env['cater.event.booking'].create({
            'partner_id': self.other_client_partner.id,
            'event_name': 'Other Event',
            'event_type': 'birthday',
            'event_date': datetime.now() + timedelta(days=15),
            'venue': 'Other Venue',
            'guest_count': 25
        })

    def test_client_can_access_own_booking(self):
        """Test that clients can access their own bookings"""
        # Switch to client user
        booking_model = self.env['cater.event.booking'].with_user(self.client_user)
        
        # Should be able to read own booking
        booking = booking_model.browse(self.client_booking.id)
        self.assertEqual(booking.id, self.client_booking.id)
        self.assertEqual(booking.event_name, 'Client Event')

    def test_client_cannot_access_other_booking(self):
        """Test that clients cannot access other clients' bookings"""
        # Switch to client user
        booking_model = self.env['cater.event.booking'].with_user(self.client_user)
        
        # Should not be able to see other booking in search
        bookings = booking_model.search([])
        booking_ids = bookings.mapped('id')
        self.assertIn(self.client_booking.id, booking_ids)
        self.assertNotIn(self.other_booking.id, booking_ids)

    def test_staff_can_access_all_bookings(self):
        """Test that staff can access all bookings"""
        # Switch to staff user
        booking_model = self.env['cater.event.booking'].with_user(self.staff_user)
        
        # Should be able to see all bookings
        bookings = booking_model.search([])
        booking_ids = bookings.mapped('id')
        self.assertIn(self.client_booking.id, booking_ids)
        self.assertIn(self.other_booking.id, booking_ids)

    def test_manager_can_access_whatsapp_config(self):
        """Test that managers can access WhatsApp configuration"""
        # Switch to manager user
        whatsapp_model = self.env['cater.whatsapp.service'].with_user(self.manager_user)
        
        # Should be able to create WhatsApp service
        service = whatsapp_model.create({
            'name': 'Test Service',
            'account_sid': 'test_sid',
            'auth_token': 'test_token',
            'from_number': '+1234567890'
        })
        self.assertTrue(service.id)

    def test_staff_cannot_access_whatsapp_config(self):
        """Test that staff cannot access WhatsApp configuration"""
        # Switch to staff user
        whatsapp_model = self.env['cater.whatsapp.service'].with_user(self.staff_user)
        
        # Should not be able to access WhatsApp services
        with self.assertRaises(AccessError):
            whatsapp_model.search([])

    def test_client_feedback_access_rules(self):
        """Test client access rules for feedback"""
        # Set booking event date to the past and state to completed
        past_date = datetime.now() - timedelta(days=7)
        self.client_booking.write({
            'state': 'completed',
            'event_date': past_date
        })
        
        # Create feedback for client booking
        feedback = self.env['cater.feedback'].create({
            'booking_id': self.client_booking.id,
            'rating': '5',
            'comments': 'Great service!'
        })
        
        # Switch to client user
        feedback_model = self.env['cater.feedback'].with_user(self.client_user)
        
        # Should be able to access own feedback
        client_feedback = feedback_model.search([])
        self.assertIn(feedback.id, client_feedback.mapped('id'))

    def test_client_cannot_delete_bookings(self):
        """Test that clients cannot delete bookings"""
        # Switch to client user
        booking_model = self.env['cater.event.booking'].with_user(self.client_user)
        
        # Should not be able to delete booking
        booking = booking_model.browse(self.client_booking.id)
        with self.assertRaises(AccessError):
            booking.unlink()

    def test_menu_item_public_access(self):
        """Test that clients can read menu items"""
        # Create menu category and item
        category = self.env['cater.menu.category'].create({
            'name': 'Test Category'
        })
        
        menu_item = self.env['cater.menu.item'].create({
            'name': 'Test Item',
            'category_id': category.id,
            'price_per_person': 25.0,
            'active': True
        })
        
        # Switch to client user
        menu_model = self.env['cater.menu.item'].with_user(self.client_user)
        
        # Should be able to read menu items
        items = menu_model.search([])
        self.assertIn(menu_item.id, items.mapped('id'))

    def test_client_cannot_modify_menu_items(self):
        """Test that clients cannot modify menu items"""
        # Create menu item as admin
        category = self.env['cater.menu.category'].create({
            'name': 'Test Category'
        })
        
        menu_item = self.env['cater.menu.item'].create({
            'name': 'Test Item',
            'category_id': category.id,
            'price_per_person': 25.0
        })
        
        # Switch to client user
        menu_model = self.env['cater.menu.item'].with_user(self.client_user)
        
        # Should not be able to modify
        item = menu_model.browse(menu_item.id)
        with self.assertRaises(AccessError):
            item.write({'price_per_person': 30.0})

    def test_accountant_can_read_bookings(self):
        """Test accountant can read bookings but not modify"""
        # Create booking as admin
        booking = self.env['cater.event.booking'].create({
            'event_name': 'Wedding Reception',
            'event_date': '2024-06-15',
            'num_guests': 150,
            'partner_id': self.client_partner.id
        })
        
        # Switch to accountant user
        booking_model = self.env['cater.event.booking'].with_user(self.accountant_user)
        
        # Should be able to read
        accountant_booking = booking_model.browse(booking.id)
        self.assertEqual(accountant_booking.event_name, 'Wedding Reception')
        
        # Should NOT be able to modify
        with self.assertRaises(AccessError):
            accountant_booking.write({'num_guests': 200})

    def test_accountant_can_manage_invoices(self):
        """Test accountant can create, read, and update invoices"""
        # Switch to accountant user
        invoice_model = self.env['account.move'].with_user(self.accountant_user)
        
        # Should be able to create invoice
        invoice = invoice_model.create({
            'partner_id': self.client_partner.id,
            'move_type': 'out_invoice',
        })
        self.assertTrue(invoice.id)
        
        # Should be able to update
        invoice.write({'ref': 'ACC-001'})
        self.assertEqual(invoice.ref, 'ACC-001')

    def test_accountant_can_manage_payments(self):
        """Test accountant can manage payments"""
        # Switch to accountant user
        payment_model = self.env['account.payment'].with_user(self.accountant_user)
        
        # Should be able to create payment
        payment = payment_model.create({
            'partner_id': self.client_partner.id,
            'amount': 1000.0,
            'payment_type': 'inbound',
            'partner_type': 'customer',
        })
        self.assertTrue(payment.id)
        self.assertEqual(payment.amount, 1000.0)

    def test_accountant_cannot_access_menu_config(self):
        """Test accountant cannot access menu configuration"""
        # Create menu item as admin
        menu_item = self.env['cater.menu.item'].create({
            'name': 'Grilled Salmon',
            'category_id': self.category.id,
            'price_per_person': 25.0
        })
        
        # Switch to accountant user
        menu_model = self.env['cater.menu.item'].with_user(self.accountant_user)
        
        # Should NOT be able to read menu items
        with self.assertRaises(AccessError):
            menu_model.browse(menu_item.id).read(['name'])

    def test_sales_order_client_access(self):
        """Test client access to sales orders"""
        # Create sale order linked to client
        sale_order = self.env['sale.order'].create({
            'partner_id': self.client_partner.id,
            'state': 'draft'
        })
        
        # Switch to client user
        sale_model = self.env['sale.order'].with_user(self.client_user)
        
        # Should be able to access own sale orders
        orders = sale_model.search([])
        self.assertIn(sale_order.id, orders.mapped('id'))
