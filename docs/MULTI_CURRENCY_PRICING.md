# Multi-Currency Pricing Guide

## Overview

The Catering Management module includes a robust multi-currency pricing system that allows you to manage event bookings in Ghana Cedis (GHS) while displaying converted amounts in USD, GBP, and other currencies. This system is designed for Odoo Community Edition with full manual control over exchange rates.

## Key Features

- **Manual Exchange Rate Management**: Full control over currency conversion rates
- **Historical Rate Tracking**: Maintain rate history with date-based lookups
- **Automatic Conversions**: Real-time conversion of booking totals
- **Flexible Display**: Toggle currency conversions on/off per booking
- **Multi-Currency Support**: Convert between GHS, USD, GBP, EUR, and more

## Architecture

### Models

#### `cater.currency.rate`

Stores manual exchange rate records with the following structure:

```python
{
    'company_id': Many2one('res.company'),  # Company context
    'currency_id': Many2one('res.currency'), # Target currency
    'company_currency_id': Many2one('res.currency'), # Base currency (GHS)
    'rate': Float,  # Direct conversion rate
    'inverse_rate': Float,  # Calculated inverse rate
    'date': Date,  # Effective date
    'active': Boolean  # Active status
}
```

#### Extended `cater.event.booking`

Added fields for multi-currency display:

```python
{
    'total_amount_usd': Monetary,  # Total in USD
    'total_amount_gbp': Monetary,  # Total in GBP
    'show_currency_conversions': Boolean,  # Display toggle
    'usd_currency_id': Many2one,  # USD currency reference
    'gbp_currency_id': Many2one   # GBP currency reference
}
```

## Managing Exchange Rates

### Accessing Exchange Rates

1. Navigate to **Event Planning → Configuration → Exchange Rates**
2. Only users with Manager role can create/edit rates
3. Staff members have read-only access

### Creating Exchange Rates

#### Method 1: Quick Create (Editable List)

1. Open Exchange Rates list view
2. Click on a blank row
3. Enter:
   - **Date**: Effective date for the rate
   - **Currency**: Target currency (USD, GBP, EUR, etc.)
   - **Rate**: Conversion rate from GHS to target currency

#### Method 2: Form View

1. Click **Create** button
2. Fill in the form:
   - **Date**: When this rate becomes effective
   - **Company Currency**: GHS (auto-filled, read-only)
   - **Currency**: Select target currency
   - **Direct Rate**: Enter the rate (e.g., 0.082 for USD)
3. **Inverse Rate** is automatically calculated
4. Click **Save**

### Understanding Exchange Rates

#### Direct Rate

The direct rate represents: **1 GHS = X target currency**

Example:

- Direct Rate: 0.082
- Meaning: 1 GHS = 0.082 USD
- To convert GHS 1000: 1000 × 0.082 = $82

#### Inverse Rate

The inverse rate represents: **1 target currency = X GHS** (auto-calculated)

Example:

- Inverse Rate: 12.195
- Meaning: 1 USD = 12.195 GHS
- To convert $100: 100 × 12.195 = GHS 1,219.50

### Current Exchange Rates (January 2026)

Pre-loaded sample rates:

| Currency | Rate (1 GHS = X) | Inverse (1 X = GHS) |
| -------- | ---------------- | ------------------- |
| USD      | 0.082            | 12.195              |
| GBP      | 0.063            | 15.873              |
| EUR      | 0.075            | 13.333              |

> **Note**: These are example rates. Update them with current market rates.

### Updating Rates

To update exchange rates:

1. **Create a new rate entry** with today's date
2. The system automatically uses the **most recent rate** based on date
3. Old rates remain in history for past bookings

**Example Workflow:**

```
Date: 2025-12-01 → 1 GHS = 0.080 USD
Date: 2026-01-01 → 1 GHS = 0.082 USD (current)
Date: 2026-02-01 → 1 GHS = 0.084 USD (future)
```

A booking dated January 15, 2026 will use the 0.082 rate.

### Rate History

- View all historical rates by removing the "Active" filter
- Archive old rates instead of deleting them
- Each date can have only one rate per currency per company

## Using Multi-Currency Display

### On Event Booking Form

1. Open any event booking
2. Scroll to the **Totals** section (bottom right)
3. Toggle **Show Currency Conversions** to ON
4. The form displays:
   - **Total Amount**: In GHS (base currency)
   - **Total (USD)**: Converted amount in US Dollars
   - **Total (GBP)**: Converted amount in British Pounds

### How Conversions Work

#### Date-Based Conversion

- Uses the **Event Date** for rate lookup
- Falls back to **Today's rate** if event date not set
- Ensures accurate historical pricing

#### Conversion Formula

For GHS → Foreign Currency:

```
Foreign Amount = GHS Amount × Direct Rate
```

For Foreign Currency → GHS:

```
GHS Amount = Foreign Amount × Inverse Rate
```

For Cross-Currency (e.g., USD → GBP):

```
1. USD → GHS (using inverse USD rate)
2. GHS → GBP (using direct GBP rate)
```

### Example Calculations

**Booking Total: GHS 5,000**

With rates: 1 GHS = 0.082 USD, 1 GHS = 0.063 GBP

- **USD Conversion**: 5,000 × 0.082 = **$410**
- **GBP Conversion**: 5,000 × 0.063 = **£315**

## Technical Implementation

### Compute Methods

#### `_compute_currency_conversions()`

```python
@api.depends('total_amount', 'currency_id', 'event_date')
def _compute_currency_conversions(self):
    """Convert total amount to USD and GBP using manual exchange rates"""
    for booking in self:
        conversion_date = booking.event_date.date() if booking.event_date else fields.Date.today()

        booking.total_amount_usd = self.env['cater.currency.rate'].convert_amount(
            booking.total_amount,
            booking.currency_id,
            usd_currency,
            conversion_date
        )
```

#### `get_conversion_rate()`

```python
@api.model
def get_conversion_rate(self, from_currency, to_currency, date=None):
    """
    Get conversion rate from one currency to another
    Returns the rate to multiply with the from_currency amount
    """
    # Handles direct, inverse, and cross-currency conversions
```

#### `convert_amount()`

```python
@api.model
def convert_amount(self, amount, from_currency, to_currency, date=None):
    """Convert an amount from one currency to another"""
    rate = self.get_conversion_rate(from_currency, to_currency, date)
    return amount * rate
```

### Conversion Logic

The system handles three conversion scenarios:

1. **Base → Foreign**: GHS → USD

   - Lookup: Direct rate from `cater.currency.rate`
   - Formula: `amount × rate`

2. **Foreign → Base**: USD → GHS

   - Lookup: Inverse rate from `cater.currency.rate`
   - Formula: `amount × inverse_rate`

3. **Foreign → Foreign**: USD → GBP
   - Two-step conversion through base currency
   - Formula: `amount × usd_inverse × gbp_direct`

## Security & Access Control

### Permission Levels

| Group   | Read | Create | Update | Delete |
| ------- | ---- | ------ | ------ | ------ |
| Manager | ✓    | ✓      | ✓      | ✓      |
| Staff   | ✓    | ✗      | ✗      | ✗      |
| Client  | ✗    | ✗      | ✗      | ✗      |

### Security Rules

- Exchange rates are company-specific
- Multi-company installations: Each company manages own rates
- Only managers can modify rates to prevent unauthorized changes
- Staff can view rates for reference

## Best Practices

### Rate Management

1. **Update Regularly**: Review and update rates weekly or monthly
2. **Use Accurate Dates**: Set effective date to when rate becomes valid
3. **Archive Old Rates**: Keep history but mark old rates as inactive
4. **Document Changes**: Use Odoo's chatter to note rate change reasons

### Data Entry

1. **Verify Rates**: Double-check rates against reliable sources (Bank of Ghana, XE.com)
2. **Consistent Decimals**: Use 6 decimal places for accuracy
3. **Test Conversions**: Create test bookings to verify calculations
4. **Bulk Updates**: Use CSV import for multiple currency updates

### Troubleshooting

#### Currency conversions showing 0.00

**Cause**: No exchange rate found for the date
**Solution**:

1. Go to Exchange Rates
2. Create a rate entry for the target currency
3. Set date to today or earlier
4. Reopen the booking form

#### Wrong conversion amounts

**Cause**: Using outdated rate
**Solution**:

1. Create new rate entry with current date
2. Ensure it's marked as Active
3. System will use most recent rate

#### Missing currencies in dropdown

**Cause**: Currency not activated in Odoo
**Solution**:

1. Go to Settings → Accounting → Currencies
2. Find and activate required currencies
3. Return to Exchange Rates and add rate

## Reporting Considerations

### Multi-Currency Reports

When generating reports:

- Base amounts always in GHS
- Converted amounts for reference only
- Use event date for historical accuracy
- Group by currency for analysis

### Export Capabilities

Export exchange rates to CSV:

1. Go to Exchange Rates list view
2. Select records (or select all)
3. Click Action → Export
4. Choose fields: Date, Currency, Rate

## API Usage

### Programmatic Conversion

```python
# Get conversion rate
rate = self.env['cater.currency.rate'].get_conversion_rate(
    from_currency=ghs_currency,
    to_currency=usd_currency,
    date='2026-01-15'
)

# Convert amount
usd_amount = self.env['cater.currency.rate'].convert_amount(
    amount=5000.00,
    from_currency=ghs_currency,
    to_currency=usd_currency,
    date='2026-01-15'
)
```

### Integration Points

- **Invoicing**: Use same rates for invoice currency conversion
- **Reporting**: Pull rates for financial reports
- **API Endpoints**: Expose rates via REST API for external systems

## Community Edition Notes

This implementation is specifically designed for **Odoo Community Edition** where:

- No automatic currency rate updates from external sources
- Full manual control over exchange rates
- No dependency on paid modules or external services
- Simple, maintainable codebase

For automatic rate updates, consider:

- Using Odoo Enterprise Edition
- Implementing custom integration with currency APIs
- Scheduled imports from Bank of Ghana

## Migration from Standard Odoo Currency Rates

If migrating from Odoo's built-in `res.currency.rate`:

```python
# Migration script example
def migrate_currency_rates(env):
    """Migrate from res.currency.rate to cater.currency.rate"""
    odoo_rates = env['res.currency.rate'].search([
        ('currency_id', 'in', [USD, GBP, EUR]),
        ('company_id', '=', env.company.id)
    ])

    for rate in odoo_rates:
        env['cater.currency.rate'].create({
            'date': rate.name,
            'currency_id': rate.currency_id.id,
            'rate': 1.0 / rate.rate if rate.rate else 0.0,
            'active': True
        })
```

## Support & Resources

### Internal Resources

- Exchange Rate list: Event Planning → Configuration → Exchange Rates
- Security settings: `security/ir.model.access.csv`
- Model definition: `models/currency_rate.py`
- View definitions: `views/currency_rate_views.xml`

### External Resources

- [Bank of Ghana Rates](https://www.bog.gov.gh/)
- [XE Currency Converter](https://www.xe.com/)
- [OANDA Historical Rates](https://www.oanda.com/currency-converter/)

## Future Enhancements

Potential improvements:

- [ ] Bulk rate import from CSV
- [ ] Integration with Bank of Ghana API
- [ ] Rate change notifications
- [ ] Automatic rate expiry warnings
- [ ] Multi-currency payment support
- [ ] Rate variance analytics
- [ ] Scheduled rate updates

## Changelog

### Version 18.0.1.0.0 (January 2026)

- Initial implementation of manual currency rate management
- Added USD and GBP conversion display on bookings
- Created exchange rate CRUD interface
- Added security rules for manager-only access
- Pre-loaded sample rates for GHS/USD/GBP/EUR

---

**Last Updated**: January 2, 2026  
**Module**: Catering Management 2.0  
**Odoo Version**: 18.0 Community Edition
