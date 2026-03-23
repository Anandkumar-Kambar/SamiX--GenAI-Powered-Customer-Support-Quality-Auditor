# SamiX Logo Assets

## How to Add Your Logo

1. **Place your logo file** in this directory as `logo.png`
   - Recommended format: PNG or JPG
   - Recommended size: 400x400px or 500x500px
   - Make sure it's transparent background (for PNG) or has appropriate background

2. **Supported locations:**
   - **Login page:** Will display at the top of the brand section
   - **Sidebar:** Will display at the top of the sidebar (scaled to 100x100px)
   - **Auto fallback:** If logo file doesn't exist, app uses a gradient badge with "S"

## Testing

Once you place your logo as `logo.png`:

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will automatically:
- Load `logo.png` on login page
- Load `logo.png` in sidebar
- Fallback to gradient badge if file not found

## Logo Specifications

- **Filename:** `logo.png` (exact name required)
- **Format:** PNG, JPG, or GIF
- **Recommended dimensions:** 
  - Login page: 400-500px width
  - Sidebar: Will auto-scale, suggested 100-200px
- **Background:** Transparent PNG recommended

## Examples

If you have a custom logo file, simply copy it here:
```
c:\Desktop\infosys\assets\images\logo.png
```

Done! The app will automatically detect and use it on next run.
