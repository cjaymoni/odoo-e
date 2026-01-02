#!/usr/bin/env python3
import odoo
from odoo import api, SUPERUSER_ID

db_name = 'catering_db'
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    bookings = env['cater.event.booking'].search([])
    print(f"Found {len(bookings)} bookings")
    for booking in bookings:
        booking._compute_currency_conversions()
        print(f"Booking {booking.name}: GHS {booking.total_amount} = USD {booking.total_amount_usd}, GBP {booking.total_amount_gbp}")
    cr.commit()
    print("Done recomputing currency conversions")
