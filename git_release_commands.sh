#!/bin/bash

# Git Commands for Bignan Mancha OMR Reader v2.0.0 Release
# Run these commands to commit and tag the release

echo "================================================"
echo "Bignan Mancha OMR Reader v2.0.0 Release"
echo "================================================"
echo ""

# Step 1: Check current status
echo "Step 1: Checking git status..."
git status
echo ""
read -p "Press Enter to continue..."

# Step 2: Add all changed files
echo ""
echo "Step 2: Adding all changed files..."
git add .
echo "✅ Files staged"
echo ""
read -p "Press Enter to continue..."

# Step 3: Show what will be committed
echo ""
echo "Step 3: Files to be committed:"
git status --short
echo ""
read -p "Press Enter to continue..."

# Step 4: Commit with detailed message
echo ""
echo "Step 4: Creating commit..."
git commit -F COMMIT_MESSAGE.txt
echo "✅ Commit created"
echo ""
read -p "Press Enter to continue..."

# Step 5: Create annotated tag
echo ""
echo "Step 5: Creating version tag v2.0.0..."
git tag -a v2.0.0 -m "Release v2.0.0: Bignan Mancha OMR Reader with Automatic Poppler Bundling

🎉 Major Release
- Application rebranded to Bignan Mancha OMR Reader
- Automatic Poppler bundling for Windows
- PDF extraction works out-of-the-box
- Enhanced error handling and documentation
- Version 2.0.0

See RELEASE_NOTES_v2.0.0.md for full details."

echo "✅ Tag v2.0.0 created"
echo ""

# Step 6: Show commit and tag info
echo "Step 6: Verifying commit and tag..."
echo ""
echo "Latest commit:"
git log -1 --oneline
echo ""
echo "Tag information:"
git tag -n5 v2.0.0
echo ""
read -p "Press Enter to continue..."

# Step 7: Push to remote
echo ""
echo "Step 7: Ready to push to remote repository"
echo ""
echo "To push the commit and tag, run:"
echo ""
echo "  git push origin main"
echo "  git push origin v2.0.0"
echo ""
echo "Or push both at once:"
echo ""
echo "  git push origin main --tags"
echo ""
read -p "Do you want to push now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Pushing to remote..."
    git push origin main
    git push origin v2.0.0
    echo ""
    echo "✅ Pushed to remote!"
else
    echo ""
    echo "ℹ️  Skipped push. You can push later with:"
    echo "  git push origin main --tags"
fi

echo ""
echo "================================================"
echo "✅ Release v2.0.0 Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Go to GitHub repository"
echo "2. Navigate to 'Releases'"
echo "3. Click 'Draft a new release'"
echo "4. Select tag: v2.0.0"
echo "5. Title: Bignan Mancha OMR Reader v2.0.0"
echo "6. Copy content from RELEASE_NOTES_v2.0.0.md"
echo "7. Attach built installers:"
echo "   - Bignan_Mancha_OMR_Reader_v2.0_Setup.exe (Windows)"
echo "   - Bignan_Mancha_OMR_Reader_v2.0.dmg (macOS)"
echo "8. Publish release"
echo ""
echo "================================================"

