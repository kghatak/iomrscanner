# 🚀 Quick Release Commands - v2.0.0

Copy and paste these commands to commit and tag the release:

---

## Option 1: Copy-Paste Commands (Fastest)

```bash
# Stage all changes
git add .

# Commit with prepared message
git commit -F COMMIT_MESSAGE.txt

# Create version tag
git tag -a v2.0.0 -m "Release v2.0.0: Bignan Mancha OMR Reader with Automatic Poppler Bundling

Major Release:
- Rebranded to Bignan Mancha OMR Reader
- Automatic Poppler bundling for Windows
- PDF extraction works out-of-the-box

See RELEASE_NOTES_v2.0.0.md for details."

# Push to remote
git push origin main --tags
```

**Done!** ✅

---

## Option 2: Interactive Script

```bash
./git_release_commands.sh
```

The script will guide you through each step.

---

## What Will Be Committed

**Modified Files (M):**
- .gitignore
- README.md
- build_config.py
- build_cross_platform.py
- main.py
- requirements.txt
- ui/main_window.py

**New Files (??):**
- Bignan Mancha OMR Reader.spec
- CHANGELOG.md
- COMMIT_MESSAGE.txt
- RELEASE_NOTES_v2.0.0.md
- download_poppler_windows.py
- pdf_utils.py
- tests/test_pdf_utils.py
- docs/WINDOWS_SETUP_GUIDE.md
- WINDOWS_BUILD_WITH_POPPLER.md
- And several documentation files...

**Deleted:**
- Image Folder Analyzer.spec (renamed)

---

## After Pushing

### Create GitHub Release

1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/releases/new

2. Fill in:
   - **Tag:** v2.0.0
   - **Title:** Bignan Mancha OMR Reader v2.0.0
   - **Description:** Paste from RELEASE_NOTES_v2.0.0.md

3. Build and attach installers:
   ```bash
   python build_cross_platform.py
   ```
   
   Upload:
   - `dist/Bignan_Mancha_OMR_Reader_v2.0_Setup.exe` (Windows)
   - `dist/Bignan_Mancha_OMR_Reader_v2.0.dmg` (macOS)

4. Check "Set as the latest release"

5. Click "Publish release"

---

## Verify

```bash
# Check commit
git log -1 --oneline

# Check tag
git tag -l

# Check remote
git ls-remote --tags origin
```

---

## Need More Details?

See: `GIT_RELEASE_GUIDE.md` for complete step-by-step instructions.

---

**Ready? Let's release v2.0.0! 🎉**

