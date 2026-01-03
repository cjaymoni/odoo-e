from odoo.tests.common import SavepointCase, tagged
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


@tagged('cater', 'views', 'ui', 'post_install', '-at_install')
class TestViews(SavepointCase):
    """Test views are properly configured and accessible"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.partner = cls.env['res.partner'].create({
            'name': 'View Test Customer',
            'mobile': '+233241234567',
            'is_catering_customer': True,
        })

    def test_booking_form_view_exists(self):
        """Test that booking form view is defined"""
        view = self.env.ref('cater.view_event_booking_form', raise_if_not_found=False)
        self.assertIsNotNone(view, "Booking form view should exist")
        
    def test_booking_tree_view_exists(self):
        """Test that booking tree view is defined"""
        view = self.env.ref('cater.view_event_booking_tree', raise_if_not_found=False)
        self.assertIsNotNone(view, "Booking tree view should exist")
        
    def test_booking_kanban_view_exists(self):
        """Test that booking kanban view is defined"""
        view = self.env.ref('cater.view_event_booking_kanban', raise_if_not_found=False)
        self.assertIsNotNone(view, "Booking kanban view should exist")
        
    def test_booking_search_view_exists(self):
        """Test that booking search view is defined"""
        view = self.env.ref('cater.view_event_booking_search', raise_if_not_found=False)
        self.assertIsNotNone(view, "Booking search view should exist")
        
    def test_menu_item_views_exist(self):
        """Test that menu item views are defined"""
        form_view = self.env.ref('cater.view_menu_item_form', raise_if_not_found=False)
        tree_view = self.env.ref('cater.view_menu_item_tree', raise_if_not_found=False)
        
        self.assertIsNotNone(form_view, "Menu item form view should exist")
        self.assertIsNotNone(tree_view, "Menu item tree view should exist")
        
    def test_feedback_views_exist(self):
        """Test that feedback views are defined"""
        form_view = self.env.ref('cater.view_feedback_form', raise_if_not_found=False)
        tree_view = self.env.ref('cater.view_feedback_tree', raise_if_not_found=False)
        
        self.assertIsNotNone(form_view, "Feedback form view should exist")
        self.assertIsNotNone(tree_view, "Feedback tree view should exist")
        
    def test_dashboard_action_exists(self):
        """Test that dashboard action is defined"""
        action = self.env.ref('cater.action_catering_dashboard', raise_if_not_found=False)
        self.assertIsNotNone(action, "Dashboard action should exist")
        
    def test_form_view_fields(self):
        """Test that form view contains expected fields"""
        booking = self.env['cater.event.booking'].create({
            'partner_id': self.partner.id,
            'event_name': 'View Test Event',
            'event_type': 'wedding',
            'event_date': datetime.now() + timedelta(days=30),
            'venue': 'Test Venue',
            'guest_count': 100,
        })
        
        # Test that we can access fields through the form view
        form_view = self.env['ir.ui.view'].search([
            ('model', '=', 'cater.event.booking'),
            ('type', '=', 'form')
        ], limit=1)
        
        self.assertTrue(form_view, "Form view should be found")
        
        # Test fields are accessible
        self.assertEqual(booking.partner_id, self.partner)
        self.assertEqual(booking.event_name, 'View Test Event')
        self.assertEqual(booking.state, 'draft')


@tagged('cater', 'dashboard', 'post_install', '-at_install')
class TestDashboard(SavepointCase):
    """Test dashboard functionality"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.partners = cls.env['res.partner'].create([
            {
                'name': f'Customer {i}',
                'mobile': f'+23324123456{i}',
                'is_catering_customer': True,
            } for i in range(5)
        ])
        
        cls.menu_item = cls.env['cater.menu.item'].create({
            'name': 'Test Menu',
            'category_id': cls.env['cater.menu.category'].create({'name': 'Test'}).id,
            'price_per_person': 20.0,
            'minimum_order': 10,
        })

    def test_dashboard_model_exists(self):
        """Test that dashboard model exists"""
        model = self.env['ir.model'].search([('model', '=', 'cater.dashboard')], limit=1)
        self.assertTrue(model, "Dashboard model should exist")
        
    def test_dashboard_data_retrieval(self):
        """Test dashboard data can be retrieved"""
        # Create test bookings
        bookings = []
        for i, partner in enumerate(self.partners):
            booking = self.env['cater.event.booking'].create({
                'partner_id': partner.id,
                'event_name': f'Dashboard Test Event {i}',
                'event_type': 'wedding',
                'event_date': datetime.now() + timedelta(days=10 + i),
                'venue': f'Venue {i}',
                'guest_count': 50,
                'state': 'confirmed' if i % 2 == 0 else 'draft',
            })
            
            # Add menu items
            self.env['cater.booking.menu.line'].create({
                'booking_id': booking.id,
                'menu_item_id': self.menu_item.id,
                'quantity': 50,
            })
            
            bookings.append(booking)
        
        # Get dashboard data
        dashboard = self.env['cater.dashboard']
        data = dashboard.get_dashboard_data()
        
        # Verify data structure
        self.assertIn('kpis', data)
        self.assertIn('total_bookings', data['kpis'])
        self.assertIn('total_revenue', data['kpis'])
        self.assertIn('active_customers', data['kpis'])
        
    def test_dashboard_kpis(self):
        """Test dashboard KPIs are calculated correctly"""
        # Create bookings in current month
        current_month_bookings = 3
        for i in range(current_month_bookings):
            booking = self.env['cater.event.booking'].create({
                'partner_id': self.partners[i].id,
                'event_name': f'KPI Test Event {i}',
                'event_type': 'birthday',
                'event_date': datetime.now() + timedelta(days=5 + i),
                'venue': f'Venue {i}',
                'guest_count': 30,
            })
            
            self.env['cater.booking.menu.line'].create({
                'booking_id': booking.id,
                'menu_item_id': self.menu_item.id,
                'quantity': 30,
            })
        
        # Get dashboard data
        dashboard = self.env['cater.dashboard']
        data = dashboard.get_dashboard_data()
        
        # Check booking count
        self.assertGreaterEqual(data['kpis']['total_bookings'], current_month_bookings)
        
        # Check revenue is calculated
        self.assertGreater(data['kpis']['total_revenue'], 0)


@tagged('cater', 'menus', 'post_install', '-at_install')
class TestMenuStructure(SavepointCase):
    """Test menu structure and access"""

    def test_main_menu_exists(self):
        """Test that main catering menu exists"""
        menu = self.env.ref('cater.menu_catering_root', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Main catering menu should exist")
        
    def test_bookings_menu_exists(self):
        """Test that bookings submenu exists"""
        menu = self.env.ref('cater.menu_catering_bookings', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Bookings menu should exist")
        
    def test_menu_items_menu_exists(self):
        """Test that menu items submenu exists"""
        menu = self.env.ref('cater.menu_catering_menu_items', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Menu items menu should exist")
        
    def test_customers_menu_exists(self):
        """Test that customers submenu exists"""
        menu = self.env.ref('cater.menu_catering_customers', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Customers menu should exist")
        
    def test_feedback_menu_exists(self):
        """Test that feedback submenu exists"""
        menu = self.env.ref('cater.menu_catering_feedback', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Feedback menu should exist")
        
    def test_configuration_menu_exists(self):
        """Test that configuration menu exists"""
        menu = self.env.ref('cater.menu_catering_configuration', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Configuration menu should exist")
        
    def test_dashboard_menu_exists(self):
        """Test that dashboard menu exists"""
        menu = self.env.ref('cater.menu_catering_dashboard', raise_if_not_found=False)
        self.assertIsNotNone(menu, "Dashboard menu should exist")
