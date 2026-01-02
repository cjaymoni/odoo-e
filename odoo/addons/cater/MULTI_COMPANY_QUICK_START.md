# 🚀 Quick Start: Multi-Company Setup for Catering Module

## ⚡ I Can't See Multi-Company Features! What Do I Do?

Follow these 5 simple steps:

---

## Step 1: Enable Developer Mode (1 minute)

1. Click **Settings** (⚙️ icon)
2. Scroll to bottom
3. Click **Activate the developer mode**

✅ Done? You should see more menu options appear.

---

## Step 2: Create Your Companies (2 minutes)

1. Go to: **Settings → Users & Companies → Companies**
2. Click **Create**
3. Fill in details:
   - **Name**: Premium Catering Ghana
   - **Currency**: GHS - Ghanaian Cedi
   - Upload a logo
4. Click **Save**
5. Repeat to create a second company (e.g., "Budget Events")

✅ Done? You should now have 2+ companies listed.

---

## Step 3: Give Yourself Access to All Companies (1 minute)

1. Go to: **Settings → Users & Companies → Users**
2. Find **your user** and click to edit
3. Under **Multi Companies**:
   - **Allowed Companies**: Select ALL companies you created ✓
   - **Default Company**: Select your main company
4. Click **Save**

✅ Done? You now have access to multiple companies!

---

## Step 4: Upgrade the Catering Module ⚠️ CRITICAL STEP (2 minutes)

**This is the most important step!** The company fields won't appear without upgrading.

### Using Odoo Interface (Easiest):

1. Go to **Apps** menu (top menu bar)
2. Remove the "Apps" filter (click the ✕ on filter)
3. Search: **"Catering"**
4. Find **"Catering Management 2.0"**
5. Click **⋮** (three dots button)
6. Select **"Upgrade"**
7. Wait for completion message
8. **Log out and log back in**
9. Press **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac) to refresh

### Using Command Line (If Docker):

```bash
# Stop containers
docker compose down

# Upgrade module
docker compose run --rm web odoo -u cater -d your_database_name --stop-after-init

# Start containers
docker compose up -d
```

Replace `your_database_name` with your actual database name.

✅ Done? Module upgraded successfully!

---

## Step 5: Verify Multi-Company Is Working (1 minute)

### 🔍 What You Should See Now:

1. **Company Switcher** (Top-Right Corner):

   - Look at the top-right of your screen
   - You should see your company name
   - Click it → Dropdown shows all your companies
   - Try switching between companies

2. **Company Fields in Forms**:

   - Go to **Catering → Bookings → All Bookings**
   - Click **Create** or open existing booking
   - Look for **"Company"** field near the top
   - It should show your current company

3. **Company Column in Lists**:
   - In any list view (bookings, menu items, etc.)
   - Click **☰** (menu icon on top-right of list)
   - Check **☑ Company** to show the column

✅ Success! You can now see company fields everywhere!

---

## 🎯 Quick Test: Create Company-Specific Menu Items

**Test 1: Create Item for Company 1**

1. Switch to **Company 1** (using company switcher)
2. Go to **Catering → Menu Management → Menu Items**
3. Click **Create**
4. Notice: **Company** field = Company 1 (auto-filled)
5. Create an item:
   - **Name**: Premium Seafood Platter
   - **Price**: GHS 150.00
6. Click **Save**

**Test 2: Create Item for Company 2**

1. Switch to **Company 2**
2. Go to **Catering → Menu Management → Menu Items**
3. Notice: You DON'T see the item you just created (data isolation works!)
4. Click **Create**
5. **Company** field = Company 2 (auto-filled)
6. Create an item:
   - **Name**: Budget Jollof Rice
   - **Price**: GHS 25.00
7. Click **Save**

**Test 3: Verify Isolation**

1. Switch back to **Company 1**
2. Go to menu items list
3. You should see "Premium Seafood" but NOT "Budget Jollof"
4. Switch to **Company 2**
5. You should see "Budget Jollof" but NOT "Premium Seafood"

✅ Perfect! Multi-company data isolation is working!

---

## ❌ Troubleshooting

### Problem: I don't see the company switcher

**Solution:**

- Your user must have access to 2+ companies
- Go back to **Step 3** above
- Make sure "Allowed Companies" has multiple companies selected
- **Log out and log back in**

### Problem: Company field not showing in forms

**Solution (90% of cases):**

- You didn't upgrade the module → Go back to **Step 4**
- Clear browser cache: Press **Ctrl+Shift+R**

**Solution (other 10%):**

- User not in multi-company group
- Settings → Users → Your User
- Look for "Multi Companies" checkbox and enable it

### Problem: "Invalid company" error when creating booking

**Solution:**

- You're mixing items from different companies
- Check: Menu item belongs to **Company A**
- But: Booking belongs to **Company B**
- Fix: Switch to correct company OR choose items from same company

### Problem: I see all data from all companies

**Solution:**

- This might be intentional if you're an admin
- Check record rules in Settings → Technical → Security → Record Rules
- Filter by model: `cater.event.booking`
- Ensure multi-company rules are active

---

## 📋 Configuration Checklist

Use this to verify everything is set up correctly:

### System Configuration

- [ ] Developer mode enabled
- [ ] 2+ companies created
- [ ] Companies have names and currency set

### User Configuration

- [ ] User has "Allowed Companies" with 2+ companies
- [ ] User has default company set
- [ ] User logged out and back in after changes

### Module Configuration

- [ ] Catering module upgraded (Step 4 completed)
- [ ] Browser cache cleared (Ctrl+Shift+R)
- [ ] Views show company fields in forms

### Verification Tests

- [ ] Company switcher visible in top-right corner
- [ ] Can switch between companies
- [ ] Company field visible in booking form
- [ ] Company field visible in menu item form
- [ ] Company field visible in services form
- [ ] Data filters when switching companies
- [ ] Created test records in different companies
- [ ] Each company only sees its own records
- [ ] Dashboard shows only current company data

---

## 🎓 What Each Company Should Configure

Once multi-company is working, configure these for each company:

### For Each Company (Switch company first!):

1. **Menu Categories** → Create company-specific categories
2. **Menu Items** → Add items with company-specific pricing
3. **Services** → Configure services available for this company
4. **WhatsApp Integration** → Set up separate Twilio account per company
5. **Pricing** → Adjust prices based on company positioning

---

## 💡 Real-World Example

**Scenario**: You run 2 catering brands:

### Company 1: Elite Catering

- **Target**: High-end corporate events
- **Menu Items**: Premium options (GHS 80-150 per person)
- **Services**: Full-service staff, premium decorations
- **WhatsApp**: +233 24 111 1111

### Company 2: Quick Bites Catering

- **Target**: Budget-friendly parties
- **Menu Items**: Affordable options (GHS 20-40 per person)
- **Services**: Basic setup, no staff
- **WhatsApp**: +233 24 222 2222

**How to set this up:**

1. Create 2 companies (Elite Catering, Quick Bites)
2. Upgrade module (Step 4)
3. Switch to "Elite Catering"
4. Add premium menu items and services
5. Configure WhatsApp with first number
6. Switch to "Quick Bites"
7. Add budget menu items and services
8. Configure WhatsApp with second number
9. Done!

Now:

- Staff assigned to "Elite Catering" only see elite items
- Staff assigned to "Quick Bites" only see budget items
- Managers with access to both can see everything

---

## 📞 Still Having Issues?

If you've followed all steps and still don't see multi-company features:

1. **Check Odoo Version**: Multi-company requires Odoo Enterprise
2. **Check Database**: Ensure it's an Enterprise database
3. **Check Logs**: Look for errors in Odoo logs
4. **Re-upgrade Module**: Sometimes need to upgrade twice

**Debug Commands:**

```python
# In Odoo shell or debug mode
# Check if multi-company is available
self.env.user.company_ids  # Should show multiple companies

# Check current company
self.env.company  # Should show current company

# Check if module is upgraded
self.env['ir.module.module'].search([('name', '=', 'cater')]).latest_version
```

---

## ✅ Success Indicators

You'll know multi-company is fully working when:

✓ Company name appears in top-right corner  
✓ Clicking it shows dropdown with all companies  
✓ Forms show "Company" field  
✓ Lists can display "Company" column  
✓ Switching companies changes visible data  
✓ Dashboard updates when switching companies  
✓ Cannot mix records from different companies  
✓ Each company has independent configuration

---

**🎉 Congratulations!** Your Catering Management System now supports multiple companies!

For detailed technical documentation, see: `MULTI_COMPANY_IMPLEMENTATION.md`
