# Exporting Design Tokens from Figma

## Your Figma File

**Link**: https://www.figma.com/make/VFSy2rtjUpuj2on68LeoRa/Create-Figma-File?node-id=0-4&t=BHQ4YP5URMk7xVfG-1

## Method 1: Manual Token Export

### Step 1: Inspect Your Design in Figma

Open your Figma file and:

1. **Select design elements** (buttons, cards, text, etc.)
2. **Note the values** in the right panel:
   - Fill colors
   - Text styles
   - Effects (shadows)
   - Layout spacing

### Step 2: Extract Color Palette

Click on any element and note the **Fill** colors:

```
Example:
- Primary Button: #2563EB
- Background: #F8FAFC
- Text: #0F172A
- Border: #E2E8F0
```

### Step 3: Extract Typography

Look at text elements and note:
- Font family (e.g., Inter, Roboto)
- Font sizes (e.g., 14px, 16px, 24px)
- Font weights (400, 500, 600, 700)
- Line heights

### Step 4: Extract Spacing

Measure spacing between elements:
- Padding values (8px, 16px, 24px)
- Margins
- Gap between items

### Step 5: Extract Other Values

- **Border radius**: 4px, 8px, 12px, 16px
- **Shadows**: Copy shadow values
- **Breakpoints**: Note mobile/tablet/desktop widths

## Method 2: Using Figma Tokens Plugin (Recommended)

### Install the Plugin

1. In Figma, go to **Plugins** → **Browse plugins in Community**
2. Search for **"Figma Tokens"** or **"Design Tokens"**
3. Install the plugin

### Export Tokens

1. Open your Figma file
2. Run the **Figma Tokens** plugin
3. The plugin will extract:
   - Colors
   - Typography
   - Spacing
   - Effects
   - Sizing
4. Export as JSON

### Alternative Plugins

- **Tokens Studio** - Most popular, exports JSON
- **Style Dictionary** - Enterprise-grade
- **Design Tokens** - Simple export

## Method 3: Using Figma's Dev Mode

If you have Figma Professional:

1. Click **Dev Mode** (toggle in top-right)
2. Select any element
3. Copy CSS values directly
4. Figma shows computed values in code format

## Method 4: Use Figma API (Advanced)

```bash
# Get your Figma API token from Account Settings
# https://www.figma.com/developers/api#access-tokens

# Install figma-api package
npm install figma-api

# Create a script to extract tokens
node scripts/extract-figma-tokens.js
```

## Method 5: Screenshot & Manual Entry

If all else fails:

1. Take screenshots of your design
2. Use a color picker tool (e.g., ColorZilla browser extension)
3. Measure spacing using browser DevTools
4. Manually enter values into `figma-tokens.json`

---

## Quick Template

Use this template and fill in your values:

```json
{
  "color": {
    "primary": { "value": "#YOUR_COLOR" },
    "secondary": { "value": "#YOUR_COLOR" },
    "accent": { "value": "#YOUR_COLOR" },
    "background": { "value": "#YOUR_COLOR" },
    "foreground": { "value": "#YOUR_COLOR" },
    "muted": { "value": "#YOUR_COLOR" },
    "card": { "value": "#YOUR_COLOR" },
    "border": { "value": "#YOUR_COLOR" }
  },
  "radius": {
    "sm": { "value": "0.25rem" },
    "md": { "value": "0.5rem" },
    "lg": { "value": "0.75rem" },
    "xl": { "value": "1rem" }
  },
  "font": {
    "heading": { "value": "YOUR_FONT, sans-serif" },
    "body": { "value": "YOUR_FONT, sans-serif" },
    "mono": { "value": "monospace" }
  },
  "fontSize": {
    "sm": { "value": "0.875rem" },
    "base": { "value": "1rem" },
    "lg": { "value": "1.125rem" },
    "xl": { "value": "1.25rem" },
    "2xl": { "value": "1.5rem" },
    "3xl": { "value": "1.875rem" }
  },
  "spacing": {
    "0": { "value": "0px" },
    "1": { "value": "4px" },
    "2": { "value": "8px" },
    "3": { "value": "12px" },
    "4": { "value": "16px" },
    "6": { "value": "24px" },
    "8": { "value": "32px" }
  },
  "shadow": {
    "sm": { "value": "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
    "md": { "value": "0 4px 6px -1px rgb(0 0 0 / 0.1)" }
  }
}
```

---

## Next Steps After Export

1. **Update** `/design/figma-tokens.json` with your values
2. **Run** `npm run tokens:apply` to regenerate CSS
3. **Preview** your changes at `http://192.168.178.50:5173`
4. **Iterate** until it matches your Figma design

## Need Help?

If you can share:
- Screenshots of your Figma design
- Specific color codes
- Font choices

I can help you create the exact token file!

