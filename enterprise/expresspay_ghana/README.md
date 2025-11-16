# ExpressPay Ghana - Odoo Payment Module

## Overview

This module integrates ExpressPay Ghana payment gateway with Odoo, providing a seamless payment experience for customers in Ghana. The module features a **hybrid webhook system** that ensures maximum reliability for both webhook-enabled and webhook-disabled environments.

## Features

- **ExpressPay Integration**: Full integration with ExpressPay Ghana payment gateway
- **Hybrid Webhook System**: Configurable webhooks with intelligent fallback polling
- **Multi-environment Support**: Test (sandbox) and production modes
- **Real-time Notifications**: Webhook support for instant payment updates
- **Mobile Money Support**: Designed for Ghana's mobile money ecosystem
- **Fallback Mechanisms**: Automatic polling when webhooks are unavailable
- **Production Ready**: Fully tested and deployed in production environments

## Configuration

### 1. Install the Module

Install the `expresspay_ghana` module in Odoo.

### 2. Configure ExpressPay Provider

Go to **Accounting > Configuration > Payment Providers** and configure the ExpressPay provider:

#### Required Fields:

- **Merchant ID**: Your ExpressPay merchant ID
- **API Key**: Your ExpressPay API key
- **Base URL for Webhooks**: The base URL for your Odoo instance

#### Advanced Configuration:

- **Enable Webhooks**: Toggle webhook notifications on/off
- **Fallback Polling**: Enable automatic status polling when webhooks are disabled

#### Webhook Configuration:

The module now supports a **hybrid approach** for maximum reliability:

- **Enable Webhooks**: When enabled, ExpressPay will send real-time payment notifications
- **Fallback Polling**: When webhooks are disabled, the system automatically polls for pending payments
- **Mobile Money Support**: Webhooks are required for mobile money payments (ExpressPay requirement)

#### Base URL Configuration:

The **Base URL for Webhooks** field is crucial for proper webhook handling:

- **Local Development**: `https://localhost:8069`
- **Production**: `https://yourdomain.com`
- **Tunnel Services**: `https://your-ngrok-url.ngrok.io`

**Important**: This URL must be accessible from the internet for ExpressPay to send webhook notifications.

### 3. Environment Settings

- **Test Mode**: Uses sandbox URLs and test credentials
- **Production Mode**: Uses production URLs and live credentials

## Payment Flow

1. **Customer Checkout**: Customer selects ExpressPay as payment method
2. **Token Generation**: Odoo submits payment details to ExpressPay API
3. **Redirect**: Customer is redirected to ExpressPay checkout page
4. **Payment Processing**: Customer completes payment on ExpressPay
5. **Dual Notification**:
   - **Webhook**: ExpressPay sends real-time payment status to Odoo
   - **Return**: Customer returns with payment confirmation
6. **Status Validation**: Odoo queries ExpressPay for final confirmation
7. **Order Completion**: Odoo processes the payment and completes the order

## Webhook Endpoints

The module automatically creates these endpoints:

- **Return URL**: `/payment/expresspay/return` - Customer return from ExpressPay
- **Webhook URL**: `/payment/expresspay/webhook` - Payment notifications from ExpressPay

## Hybrid System Architecture

### 🚀 **Three Operating Modes**

#### **Mode 1: Webhooks Enabled** (Recommended for Production)

```
✅ Enable Webhooks: ON
❌ Fallback Polling: OFF
```

- **Real-time updates** via ExpressPay webhooks
- **Most reliable** for mobile money payments
- **Requires public HTTPS endpoint**
- **Instant payment confirmations**

#### **Mode 2: Fallback Polling** (Great for Development)

```
❌ Enable Webhooks: OFF
✅ Fallback Polling: ON
```

- **No public endpoint needed**
- **Automatic status checking** every 2 minutes
- **Perfect for local development**
- **Suitable for testing environments**

#### **Mode 3: Basic Mode** (Simple but Limited)

```
❌ Enable Webhooks: OFF
❌ Fallback Polling: OFF
```

- **Relies only on customer return**
- **Simplest setup**
- **Not recommended for production use**

### 🔄 **Smart Payment Processing**

- **Intelligent Fallback**: Automatically switches between webhook and polling modes
- **Mobile Money Support**: Handles pending payments with scheduled polling
- **Error Recovery**: Graceful degradation when webhooks fail
- **Performance Optimization**: Efficient status checking and caching

## Troubleshooting

### Common Issues:

1. **Webhook Not Received**

   - Verify the Base URL is accessible from the internet
   - Check firewall settings
   - Ensure HTTPS is properly configured
   - Verify "Enable Webhooks" is checked in provider settings
   - Check Odoo logs for webhook processing errors

2. **Payment Initialization Failed**

   - Verify merchant ID and API key
   - Check ExpressPay account status
   - Review Odoo logs for detailed error messages
   - Ensure proper currency configuration (GHS)

3. **Redirect Issues**

   - Ensure the Base URL is correctly configured
   - Check for trailing slashes in the URL
   - Verify SSL certificate validity
   - Test URL accessibility from external sources

4. **Pending Payments Not Updating**

   - If webhooks are disabled, ensure "Fallback Polling" is enabled
   - Check cron job status for polling tasks
   - Verify ExpressPay API connectivity
   - Review logs for polling errors
   - Monitor transaction states in Odoo admin

5. **Webhook Processing Errors**

   - Check Odoo logs for detailed error messages
   - Verify webhook endpoint accessibility
   - Ensure proper response handling
   - Monitor HTTP status codes

### Hybrid Mode Configuration:

**Webhooks Enabled + Fallback Polling Disabled** (Recommended for production):

- Real-time payment updates via webhooks
- Most reliable for mobile money payments
- Requires public HTTPS endpoint
- Instant order processing

**Webhooks Disabled + Fallback Polling Enabled** (For development/testing):

- Automatic status polling every 2 minutes
- No public endpoint required
- Suitable for local development
- May miss some real-time updates

**Both Disabled** (Basic mode):

- Relies only on customer return
- Simplest setup but least reliable
- Not recommended for production use

### Logs

Enable debug logging in Odoo to see detailed ExpressPay integration logs:

- Look for "ExpressPay" entries in the logs
- Check for API request/response details
- Monitor webhook processing
- Track transaction state changes
- Monitor fallback polling activities

### Debug Information

The module provides comprehensive logging:

- **Payment Flow**: Step-by-step transaction processing
- **Webhook Processing**: Real-time notification handling
- **API Communication**: ExpressPay API request/response details
- **Error Handling**: Detailed error messages and stack traces
- **Performance Metrics**: Response times and processing durations

## Recent Updates & Fixes

### ✅ **Version 1.0 - Production Ready**

- **Hybrid Webhook System**: Configurable webhooks with intelligent fallbacks
- **Mobile Money Support**: Full ExpressPay Ghana integration
- **Error Handling**: Comprehensive error handling and recovery
- **Logging**: Enhanced logging for debugging and monitoring
- **Compatibility**: Support for both old and new Odoo versions
- **Performance**: Optimized payment processing and validation

### 🔧 **Technical Improvements**

- **Field Compatibility**: Smart detection of `provider_reference` vs `acquirer_reference`
- **Response Handling**: Support for both `result` and `response-code` fields
- **State Management**: Enhanced transaction state mapping
- **Fallback Mechanisms**: Intelligent polling for pending payments
- **Webhook Reliability**: Proper HTTP response handling

## Production Deployment

### 🚀 **Ready for Production**

The module has been thoroughly tested and is ready for production deployment:

- **Stable**: All critical bugs have been resolved
- **Scalable**: Handles multiple concurrent payments
- **Reliable**: Hybrid system ensures payment reliability
- **Maintainable**: Comprehensive logging and error handling
- **Secure**: Proper authentication and validation

### 📋 **Deployment Checklist**

- [ ] Configure production merchant ID and API key
- [ ] Set production base URL for webhooks
- [ ] Enable webhooks for production environment
- [ ] Test payment flow in production mode
- [ ] Monitor logs for any issues
- [ ] Configure monitoring and alerting

## Support

For technical support or questions about this module:

- **Documentation**: Refer to ExpressPay Ghana API documentation
- **Logs**: Check Odoo logs for detailed error information
- **Configuration**: Verify all provider settings are correct
- **Testing**: Test in sandbox mode before going live

## License

This module is licensed under LGPL-3.

---

**Status**: ✅ Production Ready  
**Last Updated**: August 2025  
**Version**: 1.0  
**Odoo Compatibility**: 18.0+
