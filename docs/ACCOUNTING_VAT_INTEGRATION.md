# Accounting, VAT, and Invoice Integration

## Overview

The Catering Management System provides comprehensive accounting integration with automated invoice generation and Ghana VAT compliance. This system enables seamless transition from event bookings to financial records, ensuring accurate revenue tracking and tax reporting.

## Features

### 1. Automated Invoice Generation

- One-click invoice creation from confirmed bookings
- Automatic transfer of menu items and services to invoice lines
- Event details included in invoice narration
- Bidirectional linking between bookings and invoices

### 2. Ghana VAT Compliance (15%)

- Pre-configured Ghana VAT tax records
- Automatic VAT application on all invoice lines
- Separate tracking for sales and purchase VAT
- VAT-compliant reporting through Odoo's tax reports

### 3. Multi-Currency Support

- Base currency: GHS (Ghana Cedis)
- Currency conversions: USD, GBP, EUR
- Manual exchange rate management
- Historical rate tracking for accurate reporting

### 4. Financial Flow Integration

- Booking → Invoice → Journal Entry → Tax Report
- Automated accounting entries on invoice posting
- Real-time balance tracking
- Payment reconciliation support

## Configuration

### Ghana VAT Taxes

The system includes two pre-configured VAT tax records:

**Sales VAT (15%)**

- **Name**: Ghana VAT 15% (Sales)
- **XML ID**: `ghana_vat_sale_15`
- **Amount**: 15%
- **Type**: Sales Tax
- **Scope**: Applied to customer invoices

**Purchase VAT (15%)**

- **Name**: Ghana VAT 15% (Purchase)
- **XML ID**: `ghana_vat_purchase_15`
- **Amount**: 15%
- **Type**: Purchase Tax
- **Scope**: Applied to vendor bills

### Tax Configuration Location

Navigate to: **Accounting → Configuration → Taxes**

Both taxes are automatically created during module installation and can be modified if needed:

- Adjust tax percentage
- Change tax accounts
- Update tax applicability
- Configure tax groups

## Usage Guide

### Creating an Invoice from a Booking

#### Step 1: Confirm the Booking

Before creating an invoice, ensure the booking is confirmed:

1. Open the event booking
2. Add menu items and services
3. Click **Confirm Booking**
4. Status changes to "Confirmed"

#### Step 2: Generate Invoice

1. Click the **Create Invoice** button in the header
2. System automatically:
   - Creates draft invoice
   - Transfers all menu items as invoice lines
   - Transfers all services as invoice lines
   - Applies 15% Ghana VAT to each line
   - Links invoice to booking
   - Includes event details (date, name, guest count)

#### Step 3: Review and Post

1. Review the generated invoice
2. Verify line items and VAT calculation
3. Click **Confirm** to post the invoice
4. Journal entries are automatically created

### Viewing Booking Invoices

**Smart Button Method:**

- Click the **Invoices** smart button (shows count)
- View all invoices linked to the booking

**Manual Navigation:**

- Navigate to: **Accounting → Customers → Invoices**
- Search by booking reference or customer name

### Invoice Information

Each invoice includes:

- **Customer**: From booking partner
- **Invoice Date**: Booking creation date
- **Due Date**: Calculated based on payment terms
- **Reference**: Booking reference number
- **Event Details**: Date, name, guest count
- **Line Items**:
  - Menu items with quantities and prices
  - Services with quantities and prices
  - 15% VAT on each line
- **Total**: Subtotal + VAT

## Complete Accounting Flow

### 1. Booking Creation

```
Event Booking (Draft)
├── Menu Items (GHS pricing)
├── Services (GHS pricing)
├── Total Amount (computed)
└── Deposit Amount
```

### 2. Booking Confirmation

```
Status: Draft → Confirmed
├── Validates pricing
├── Locks menu/service items
└── Enables invoice generation
```

### 3. Invoice Generation

```
Create Invoice (Draft)
├── Transfer Menu Items → Invoice Lines
├── Transfer Services → Invoice Lines
├── Apply Ghana VAT 15%
├── Link to Booking (catering_booking_id)
└── Set Customer from Partner
```

### 4. Invoice Posting

```
Post Invoice (Confirmed)
├── Generate Journal Entry
│   ├── Debit: Accounts Receivable
│   ├── Credit: Revenue Account
│   └── Credit: VAT Payable
├── Update Customer Balance
└── Enable Payment Recording
```

### 5. Payment Recording

```
Register Payment
├── Debit: Bank/Cash Account
├── Credit: Accounts Receivable
├── Reconcile Invoice
└── Update Booking Balance
```

### 6. VAT Reporting

```
Tax Report (Periodic)
├── Collect VAT from Sales Invoices
├── Collect VAT from Purchase Bills
├── Calculate Net VAT Payable
└── Generate Compliance Report
```

## Journal Entries

### Invoice Posting Entry

When an invoice is posted, Odoo creates:

```
Journal Entry: Customer Invoice
Date: Invoice Date
Reference: INV/2024/XXXX

Account                          Debit       Credit
--------------------------------------------------
Accounts Receivable (Partner)   ₵1,150.00
Revenue - Catering Services                  ₵1,000.00
VAT Payable - 15%                            ₵150.00
--------------------------------------------------
Total                            ₵1,150.00   ₵1,150.00
```

### Payment Entry

When payment is recorded:

```
Journal Entry: Customer Payment
Date: Payment Date
Reference: Payment Reference

Account                          Debit       Credit
--------------------------------------------------
Bank/Cash Account                ₵1,150.00
Accounts Receivable (Partner)                ₵1,150.00
--------------------------------------------------
Total                            ₵1,150.00   ₵1,150.00
```

## VAT Reporting

### Accessing Tax Reports

Navigate to: **Accounting → Reporting → Tax Report**

### Report Contents

The tax report shows:

- **Sales VAT Collected**: 15% from customer invoices
- **Purchase VAT Paid**: 15% from vendor bills
- **Net VAT Position**: Amount payable/refundable
- **Period**: Selected date range

### VAT Calculation Example

```
Booking Total: ₵1,000.00
Menu Items:    ₵600.00
Services:      ₵400.00

VAT Calculation:
Menu VAT:      ₵600.00 × 15% = ₵90.00
Service VAT:   ₵400.00 × 15% = ₵60.00
Total VAT:     ₵150.00

Invoice Total: ₵1,150.00
```

## Multi-Currency Integration

### Currency Conversions

Bookings display converted amounts in USD and GBP:

- Base amount in GHS
- Converted USD amount (rate displayed)
- Converted GBP amount (rate displayed)

### Exchange Rate Management

Navigate to: **Catering → Configuration → Currency Rates**

#### Creating Exchange Rates

1. Click **New**
2. Select currency (USD, GBP, EUR)
3. Enter exchange rate (GHS → Foreign)
4. Set effective date
5. Mark as active
6. Save

#### Rate Application

- Rates are date-sensitive
- System uses rate valid on or before event date
- Multiple rates can exist for different dates
- Inactive rates are ignored

### Invoice Currency

Invoices are created in GHS (base currency) regardless of displayed conversions. Currency conversions are for display and reference only.

## Troubleshooting

### Invoice Not Creating

**Problem**: "Create Invoice" button clicked but no invoice appears

**Solutions**:

1. **Check booking status**: Must be "Confirmed", "In Progress", or "Completed"
2. **Verify line items**: Ensure menu items or services exist
3. **Check permissions**: User needs invoice creation rights
4. **Review logs**: Check Odoo logs for errors
5. **Validate partner**: Ensure customer is set on booking

### VAT Not Applied

**Problem**: Invoice lines don't have VAT

**Solutions**:

1. **Verify tax exists**: Navigate to Accounting → Configuration → Taxes
2. **Check tax active**: Ensure "Ghana VAT 15% (Sales)" is active
3. **Review XML ID**: Confirm `ghana_vat_sale_15` exists
4. **Upgrade module**: Run module upgrade if taxes are missing
5. **Check line items**: VAT should appear in "Taxes" column

### Wrong VAT Amount

**Problem**: VAT calculation seems incorrect

**Solutions**:

1. **Verify tax percentage**: Should be 15%
2. **Check price inclusion**: VAT should not be included in price
3. **Review line items**: Each line should show 15% tax separately
4. **Validate computation**: Subtotal × 0.15 = VAT amount
5. **Check rounding**: Minor differences may be due to rounding

### Invoice Not Linked to Booking

**Problem**: Smart button shows 0 invoices

**Solutions**:

1. **Check invoice field**: Open invoice, verify "Catering Booking" field is set
2. **Manual linking**: Edit invoice, set "Catering Booking" field
3. **Database check**: Verify `catering_booking_id` in invoice record
4. **Recompute**: Save booking to trigger invoice count recomputation

### Journal Entry Issues

**Problem**: Journal entry not created or incorrect

**Solutions**:

1. **Post the invoice**: Entries only created when invoice is posted
2. **Check accounts**: Verify revenue and VAT accounts are configured
3. **Review fiscal position**: Ensure correct tax mapping
4. **Validate currency**: Base currency should match invoice currency
5. **Check date**: Ensure fiscal period is open

## API Reference

### Creating Invoice (Python)

```python
# From booking record
booking = env['cater.event.booking'].browse(booking_id)
invoice = booking.action_create_invoice()

# Returns: account.move record (draft invoice)
```

### Accessing Linked Invoices

```python
# Get all invoices for a booking
booking = env['cater.event.booking'].browse(booking_id)
invoices = booking.invoice_ids

# Get invoice count
count = booking.invoice_count

# View invoices action
action = booking.action_view_invoices()
```

### Manual Invoice Creation

```python
# Get Ghana VAT tax
ghana_vat = env.ref('cater.ghana_vat_sale_15')

# Create invoice manually
invoice = env['account.move'].create({
    'move_type': 'out_invoice',
    'partner_id': partner_id,
    'catering_booking_id': booking_id,
    'invoice_date': fields.Date.today(),
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Menu Item',
            'quantity': 10,
            'price_unit': 50.00,
            'tax_ids': [(6, 0, ghana_vat.ids)],
        })
    ],
})
```

### Tax Computation

```python
# Get VAT tax record
vat_tax = env.ref('cater.ghana_vat_sale_15')

# Compute taxes for amount
taxes = vat_tax.compute_all(
    price_unit=100.00,
    currency=env.company.currency_id,
    quantity=1.0,
)

# Access computed values
subtotal = taxes['total_excluded']  # 100.00
vat_amount = taxes['total_included'] - taxes['total_excluded']  # 15.00
total = taxes['total_included']  # 115.00
```

## Best Practices

### 1. Invoice Timing

- Create invoices after booking confirmation
- Generate invoices before event date
- Post invoices within same fiscal period as event

### 2. VAT Management

- Review tax reports monthly
- Reconcile VAT accounts regularly
- File VAT returns on time
- Keep tax configuration consistent

### 3. Payment Recording

- Record deposits immediately after receipt
- Register final payments promptly
- Reconcile bank statements regularly
- Track outstanding balances

### 4. Multi-Currency

- Update exchange rates weekly
- Use consistent rate sources
- Document rate changes
- Review currency conversions periodically

### 5. Audit Trail

- Don't delete posted invoices
- Use credit notes for corrections
- Maintain proper documentation
- Keep booking-invoice links intact

## Security and Permissions

### Required Access Rights

**Invoice Creation**:

- Catering Manager or Accountant
- Account Move: Create access
- Account Move Line: Create access

**Invoice Posting**:

- Accountant or Billing role
- Account Move: Write access
- Journal: Post entries permission

**Tax Management**:

- Accountant role
- Tax configuration access
- Tax report viewing rights

### Recommended Separation

- **Sales Team**: Create bookings, generate invoices (draft)
- **Accounting Team**: Post invoices, record payments, manage taxes
- **Manager**: Full access, reporting, reconciliation

## Integration Notes

### Related Modules

The accounting integration works with:

- **account**: Core accounting functionality
- **sale**: Sales order integration
- **payment**: Payment processing
- **account_tax**: Tax computation engine

### Custom Development

When extending accounting features:

1. Inherit `account.move` for custom invoice logic
2. Extend `cater.event.booking` for additional financial fields
3. Use `account.move.line` for line-level customizations
4. Create custom tax configurations if needed

### Data Migration

When migrating from other systems:

1. Import historical bookings first
2. Create invoices with correct dates
3. Match existing journal entries
4. Reconcile opening balances
5. Validate VAT calculations

## Reporting

### Available Reports

1. **Invoice Analysis**: Accounting → Reporting → Invoices Analysis
2. **Tax Report**: Accounting → Reporting → Tax Report
3. **Partner Ledger**: Accounting → Reporting → Partner Ledger
4. **Aged Receivables**: Accounting → Reporting → Aged Receivable
5. **General Ledger**: Accounting → Reporting → General Ledger

### Custom Reports

Create custom reports for:

- Revenue by event type
- VAT collected by period
- Outstanding bookings
- Payment collection rates
- Currency conversion analysis

## Compliance

### Ghana Tax Compliance

The system is configured for Ghana tax regulations:

- Standard VAT rate: 15%
- Tax invoices include required details
- VAT registration number supported
- Compliant tax reporting format

### Audit Requirements

Maintain records for:

- All posted invoices (7+ years)
- Journal entries and supporting documents
- Tax calculations and filings
- Payment receipts and bank statements
- Currency conversion rates used

## Support and Resources

### Documentation

- [Multi-Currency Pricing Guide](MULTI_CURRENCY_PRICING.md)
- [Multi-Company Implementation](MULTI_COMPANY_IMPLEMENTATION.md)
- [Odoo Accounting Documentation](https://www.odoo.com/documentation/18.0/applications/finance/accounting.html)

### Common Tasks

- **Modify VAT rate**: Edit tax record in Accounting → Configuration → Taxes
- **Change invoice accounts**: Configure in Accounting → Configuration → Settings
- **Add payment terms**: Accounting → Configuration → Payment Terms
- **Configure invoice layout**: Settings → Companies → Document Layout

### Getting Help

1. Review error logs in Odoo debug mode
2. Check booking and invoice status
3. Verify tax configuration
4. Consult Odoo accounting documentation
5. Contact system administrator

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Module**: cater (Catering Management System)  
**Odoo Version**: 18.0 Enterprise
