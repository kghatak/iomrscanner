# Git Release Guide - v2.0.0

Step-by-step guide to commit and tag the v2.0.0 release.

---

## Quick Commands

If you're comfortable with git, here are the commands:

```bash
# 1. Stage all changes
git add .

# 2. Commit with detailed message
git commit -F COMMIT_MESSAGE.txt

# 3. Create annotated tag
git tag -a v2.0.0 -m "Release v2.0.0: Bignan Mancha OMR Reader with Automatic Poppler Bundling"

# 4. Push to remote
git push origin main
git push origin v2.0.0

# Or push both at once
git push origin main --tags
```

---

## Detailed Step-by-Step Guide

### Step 1: Check Current Status

```bash
git status
```

**Expected output:** List of modified and new files
- ✅ Modified: build_config.py, main.py, ui/main_window.py, etc.
- ✅ New: download_poppler_windows.py, pdf_utils.py, docs/WINDOWS_SETUP_GUIDE.md, etc.
- ✅ Renamed: Image Folder Analyzer.spec → Bignan Mancha OMR Reader.spec

---

### Step 2: Stage All Changes

```bash
git add .
```

This stages all modified, new, and deleted files.

**Verify:**
```bash
git status
```

Should show files in "Changes to be committed" section.

---

### Step 3: Review Changes (Optional)

See what's changed:
```bash
git diff --cached --stat
```

See detailed diff:
```bash
git diff --cached
```

---

### Step 4: Commit Changes

Use the prepared commit message:
```bash
git commit -F COMMIT_MESSAGE.txt
```

**OR** if you prefer to edit the message:
```bash
git commit
```

The default editor will open with the message from COMMIT_MESSAGE.txt.

**Verify commit:**
```bash
git log -1
```

---

### Step 5: Create Version Tag

Create an annotated tag for v2.0.0:

```bash
git tag -a v2.0.0 -m "Release v2.0.0: Bignan Mancha OMR Reader with Automatic Poppler Bundling

🎉 Major Release
- Application rebranded to Bignan Mancha OMR Reader
- Automatic Poppler bundling for Windows
- PDF extraction works out-of-the-box
- Enhanced error handling and documentation
- Version 2.0.0

See RELEASE_NOTES_v2.0.0.md for full details."
```

**Verify tag:**
```bash
git tag -l -n5 v2.0.0
```

**Show tag details:**
```bash
git show v2.0.0
```

---

### Step 6: Push to Remote

#### Option A: Push commit and tag separately
```bash
# Push the commit
git push origin main

# Push the tag
git push origin v2.0.0
```

#### Option B: Push both at once
```bash
git push origin main --tags
```

---

### Step 7: Verify on GitHub

1. Go to your GitHub repository
2. Check the commit appears in the main branch
3. Go to "Tags" tab - verify v2.0.0 is there
4. Check "Releases" - tag should be listed (draft release)

---

## Creating GitHub Release

After pushing the tag:

### Step 1: Navigate to Releases
1. Go to your GitHub repository
2. Click on "Releases" (right sidebar)
3. Click "Draft a new release"

### Step 2: Configure Release
- **Tag:** Select `v2.0.0`
- **Release title:** `Bignan Mancha OMR Reader v2.0.0`
- **Description:** Copy content from `RELEASE_NOTES_v2.0.0.md`

### Step 3: Attach Binaries

Build the installers first:
```bash
python build_cross_platform.py
```

Then attach:
- ✅ `Bignan_Mancha_OMR_Reader_v2.0_Setup.exe` (Windows)
- ✅ `Bignan_Mancha_OMR_Reader_v2.0.dmg` (macOS)
- ✅ `Bignan_Mancha_OMR_Reader_v2.0.AppImage` (Linux, if available)

### Step 4: Publish

- ✅ Check "Set as the latest release"
- ✅ Click "Publish release"

---

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Create and push commit
git add .
git commit -F COMMIT_MESSAGE.txt
git push origin main

# Create and push tag
git tag -a v2.0.0 -F RELEASE_NOTES_v2.0.0.md
git push origin v2.0.0

# Create GitHub release
gh release create v2.0.0 \
  --title "Bignan Mancha OMR Reader v2.0.0" \
  --notes-file RELEASE_NOTES_v2.0.0.md \
  dist/Bignan_Mancha_OMR_Reader_v2.0_Setup.exe \
  dist/Bignan_Mancha_OMR_Reader_v2.0.dmg
```

---

## Automated Script

For convenience, I've created an automated script:

```bash
chmod +x git_release_commands.sh
./git_release_commands.sh
```

This script will guide you through each step interactively.

---

## Rollback (If Needed)

If you need to undo:

### Undo commit (before push)
```bash
git reset --soft HEAD~1
```

### Delete tag (before push)
```bash
git tag -d v2.0.0
```

### Delete remote tag (after push)
```bash
git push origin :refs/tags/v2.0.0
```

---

## Files Changed Summary

### New Files Created
- download_poppler_windows.py
- pdf_utils.py
- tests/test_pdf_utils.py
- docs/WINDOWS_SETUP_GUIDE.md
- WINDOWS_BUILD_WITH_POPPLER.md
- WINDOWS_PDF_FIX.md
- ANSWER_WINDOWS_BUNDLE_POPPLER.md
- CHANGELOG.md
- RELEASE_NOTES_v2.0.0.md
- COMMIT_MESSAGE.txt
- git_release_commands.sh
- GIT_RELEASE_GUIDE.md (this file)
- APP_NAME_CHANGE_SUMMARY.md

### Modified Files
- build_config.py
- main.py
- ui/main_window.py
- build_cross_platform.py
- README.md
- requirements.txt
- .gitignore

### Renamed Files
- Image Folder Analyzer.spec → Bignan Mancha OMR Reader.spec

---

## Commit Statistics

Expected statistics:
- **Files changed:** ~20-25 files
- **Insertions:** ~2000+ lines
- **Deletions:** ~50-100 lines

---

## Tag Format

Tags follow semantic versioning:
- **v2.0.0** - Major release (breaking changes or major features)
- **v2.1.0** - Minor release (new features, backward compatible)
- **v2.0.1** - Patch release (bug fixes)

---

## Changelog Entry

The CHANGELOG.md has been updated with v2.0.0 details. Make sure to review it before committing.

---

## Post-Release Checklist

After publishing the release:

- [ ] Verify release appears on GitHub
- [ ] Test download links work
- [ ] Update any external documentation
- [ ] Announce the release (if applicable)
- [ ] Update version badges in README (if used)
- [ ] Create social media posts (if applicable)
- [ ] Notify existing users via email (if applicable)

---

## Need Help?

### Common Issues

**Issue:** "fatal: tag 'v2.0.0' already exists"
```bash
# Delete existing tag
git tag -d v2.0.0

# Create new tag
git tag -a v2.0.0 -m "Your message"
```

**Issue:** "Permission denied" when pushing
```bash
# Check remote URL
git remote -v

# Update remote URL if needed
git remote set-url origin https://github.com/username/repo.git
```

**Issue:** "Updates were rejected"
```bash
# Pull latest changes first
git pull origin main --rebase

# Then push
git push origin main --tags
```

---

## Summary

✅ **Stage changes:** `git add .`  
✅ **Commit:** `git commit -F COMMIT_MESSAGE.txt`  
✅ **Tag:** `git tag -a v2.0.0 -m "Release message"`  
✅ **Push:** `git push origin main --tags`  
✅ **Create GitHub Release:** Copy RELEASE_NOTES_v2.0.0.md  
✅ **Attach Installers:** Build and upload binaries  

**You're ready to release! 🚀**

---

**Version:** 2.0.0  
**Date:** October 11, 2025  
**Status:** Ready for Release

