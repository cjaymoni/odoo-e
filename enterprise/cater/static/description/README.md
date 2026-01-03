# Module Icon and Screenshots

This directory contains the visual assets for the Catering Management System module.

## Required Files

1. **icon.png** (256x256px) - Main module icon displayed in Odoo Apps
2. **banner.png** (560x280px) - Banner image for app store listing
3. **screenshot_dashboard.png** - Dashboard with KPIs and analytics
4. **screenshot_booking.png** - Booking management interface
5. **screenshot_menu.png** - Menu catalog and management
6. **screenshot_feedback.png** - Customer feedback system

## Design Guidelines

### Icon (icon.png)

- Size: 256x256 pixels
- Format: PNG with transparency
- Theme: Catering/food related (e.g., chef hat, plate with utensils, fork & knife)
- Colors: Professional colors matching Ghanaian culture
- Style: Modern, flat design

### Banner (banner.png)

- Size: 560x280 pixels
- Format: PNG
- Content: Module name + tagline + key visual
- Typography: Clear, professional fonts
- Brand: "Catering Management System for Odoo 18"

### Screenshots

- Size: Minimum 1024x768 pixels
- Format: PNG or JPG
- Quality: High resolution, clear UI elements
- Content: Real data (use demo data)
- Annotations: Optional highlights of key features

## TODO: Replace Placeholders

Currently using placeholder text files. Replace with actual images before App Store submission:

```bash
# Example using ImageMagick to create placeholder images
convert -size 256x256 xc:lightblue -gravity center -pointsize 24 \
    -annotate +0+0 "Cater\nIcon" icon.png

convert -size 560x280 xc:lightgreen -gravity center -pointsize 32 \
    -annotate +0+0 "Catering Management System" banner.png
```

## Resources for Icon Creation

- Flaticon: https://www.flaticon.com/
- Icons8: https://icons8.com/
- Canva: https://www.canva.com/
- GIMP: https://www.gimp.org/ (free)
- Adobe Photoshop/Illustrator (paid)

## Screenshot Capture

1. Start Odoo with demo data
2. Navigate to each view
3. Use browser screenshot tools or:
   - macOS: Cmd+Shift+4
   - Windows: Windows+Shift+S
   - Linux: Flameshot, Shutter, or GNOME Screenshot
