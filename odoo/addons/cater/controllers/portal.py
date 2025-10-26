# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CateringPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'booking_count' in counters:
            booking_count = request.env['cater.event.booking'].search_count([
                ('partner_id.user_ids', 'in', [request.env.user.id])
            ])
            values['booking_count'] = booking_count
            
        if 'feedback_count' in counters:
            feedback_count = request.env['cater.feedback'].search_count([
                ('booking_id.partner_id.user_ids', 'in', [request.env.user.id])
            ])
            values['feedback_count'] = feedback_count
            
        if 'menu_count' in counters:
            menu_count = request.env['cater.menu.item'].search_count([
                ('active', '=', True)
            ])
            values['menu_count'] = menu_count
        
        return values

    @http.route(['/my/bookings', '/my/bookings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_bookings(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='event_name', **kw):
        values = self._prepare_portal_layout_values()
        
        BookingModel = request.env['cater.event.booking']
        domain = [('partner_id.user_ids', 'in', [request.env.user.id])]
        
        if date_begin and date_end:
            domain += [('event_date', '>=', date_begin), ('event_date', '<=', date_end)]
        
        if search and search_in:
            search_domain = []
            if search_in in ('event_name', 'all'):
                search_domain = ['|'] + search_domain + [('event_name', 'ilike', search)]
            if search_in in ('venue', 'all'):
                search_domain = ['|'] + search_domain + [('venue', 'ilike', search)]
            domain += search_domain

        # Sorting options
        searchbar_sortings = {
            'date': {'label': 'Event Date', 'order': 'event_date desc'},
            'name': {'label': 'Event Name', 'order': 'event_name'},
            'venue': {'label': 'Venue', 'order': 'venue'},
            'state': {'label': 'Status', 'order': 'state'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Search filters
        searchbar_filters = {
            'all': {'label': 'All', 'domain': []},
            'confirmed': {'label': 'Confirmed', 'domain': [('state', '=', 'confirmed')]},
            'completed': {'label': 'Completed', 'domain': [('state', '=', 'completed')]},
        }
        
        # Count bookings
        booking_count = BookingModel.search_count(domain)
        
        # Pager
        pager = portal_pager(
            url="/my/bookings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=booking_count,
            page=page,
            step=10
        )
        
        # Get bookings
        bookings = BookingModel.search(domain, order=order, limit=10, offset=pager['offset'])
        request.session['my_bookings_history'] = bookings.ids[:100]
        
        values.update({
            'bookings': bookings,
            'page_name': 'catering_bookings',
            'pager': pager,
            'default_url': '/my/bookings',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        
        return request.render("cater.portal_my_bookings", values)

    @http.route(['/my/feedback', '/my/feedback/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_feedback(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        
        FeedbackModel = request.env['cater.feedback']
        domain = [('booking_id.partner_id.user_ids', 'in', [request.env.user.id])]
        
        feedback_count = FeedbackModel.search_count(domain)
        pager = portal_pager(
            url="/my/feedback",
            total=feedback_count,
            page=page,
            step=10
        )
        
        feedback = FeedbackModel.search(domain, order='feedback_date desc', limit=10, offset=pager['offset'])
        
        values.update({
            'feedback': feedback,
            'page_name': 'catering_feedback',
            'pager': pager,
            'default_url': '/my/feedback',
        })
        
        return request.render("cater.portal_my_feedback", values)

    @http.route(['/my/menu', '/my/menu/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_menu(self, page=1, category=None, **kw):
        values = self._prepare_portal_layout_values()
        
        MenuModel = request.env['cater.menu.item']
        domain = [('active', '=', True)]
        
        if category:
            domain += [('category_id', '=', int(category))]
        
        menu_count = MenuModel.search_count(domain)
        pager = portal_pager(
            url="/my/menu",
            url_args={'category': category},
            total=menu_count,
            page=page,
            step=12
        )
        
        menu_items = MenuModel.search(domain, order='category_id, name', limit=12, offset=pager['offset'])
        categories = request.env['cater.menu.category'].search([])
        
        values.update({
            'menu_items': menu_items,
            'categories': categories,
            'page_name': 'catering_menu',
            'pager': pager,
            'default_url': '/my/menu',
            'selected_category': int(category) if category else None,
        })
        
        return request.render("cater.portal_my_menu", values)
