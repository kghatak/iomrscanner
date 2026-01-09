# Installing Tesseract OCR for OMR Exam Reader (Windows)

If you see the error: **"OCR Error: tesseract is not installed or it's not in your PATH"**, follow these simple steps to install Tesseract OCR.

## Step-by-Step Installation

### Step 1: Download Tesseract OCR

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (usually named `tesseract-ocr-w64-setup-5.x.x.exe`)

### Step 2: Install Tesseract

1. **Run the downloaded installer**
2. **Important**: During installation, check the option **"Add Tesseract to PATH"** or **"Add to PATH"**
   - This is usually on the "Choose Components" screen
   - If you miss this, you can still install and we'll handle it in Step 3
3. **Install to default location**: `C:\Program Files\Tesseract-OCR` (recommended)
4. Complete the installation

### Step 3: Verify Installation

1. Open **Command Prompt** (Press `Win + R`, type `cmd`, press Enter)
2. Type: `tesseract --version`
3. Press Enter
4. You should see version information (e.g., "tesseract 5.x.x")

**If you see "tesseract is not recognized"**, Tesseract was not added to PATH. See "Alternative: Manual PATH Configuration" below.

### Step 4: Restart the Application

Close and reopen **OMR Exam Reader**. The application will automatically detect Tesseract and OCR should now work!

---

## Alternative: Manual PATH Configuration

If Tesseract is installed but not in PATH, you need to add it manually:

### Option A: Add to PATH (Recommended)

1. Press `Win + X` and select **"System"** (or right-click "This PC" → Properties)
2. Click **"Advanced system settings"**
3. Click **"Environment Variables"**
4. Under **"System variables"**, find and select **"Path"**, then click **"Edit"**
5. Click **"New"** and add: `C:\Program Files\Tesseract-OCR`
6. Click **"OK"** on all dialogs
7. **Restart your computer** (or restart the application)

**How to Check PATH Variable:**
- Open Command Prompt (Press `Win + R`, type `cmd`, press Enter)
- Type: `echo %PATH%` and press Enter
- This will show all directories in your PATH (separated by semicolons)
- Look for `C:\Program Files\Tesseract-OCR` in the output

### Option B: Install to Default Location (Easier)

Simply reinstall Tesseract and make sure to check **"Add to PATH"** during installation. The default location `C:\Program Files\Tesseract-OCR` is automatically detected even without PATH.

---

## Troubleshooting

### "tesseract is not recognized" in Command Prompt

- Tesseract is not in your PATH
- Solution: Follow "Alternative: Manual PATH Configuration" above, or reinstall and check "Add to PATH"

### Application still shows error after installation

1. **Close the application completely**
2. **Restart the application**
3. The app should automatically detect Tesseract at: `C:\Program Files\Tesseract-OCR`

### Check if Tesseract is installed correctly

1. Open File Explorer
2. Navigate to: `C:\Program Files\Tesseract-OCR`
3. You should see:
   - `tesseract.exe`
   - `tessdata` folder
   - Various `.dll` files

If these files exist, Tesseract is installed correctly. The application should detect it automatically.

---

## Quick Summary

1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR` (default)
3. Check "Add to PATH" during installation (optional but recommended)
4. Restart OMR Exam Reader
5. Done! OCR should now work.

---

**Need Help?** If you continue to have issues, verify:
- Tesseract is installed at: `C:\Program Files\Tesseract-OCR`
- `tesseract.exe` exists in that folder
- You've restarted the application after installation

