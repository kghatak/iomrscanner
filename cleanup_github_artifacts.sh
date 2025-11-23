#!/bin/bash
# Script to clean up old GitHub Actions artifacts
# This helps free up storage quota when it's exceeded

# You need a GitHub Personal Access Token with 'actions:write' permission
# Create one at: https://github.com/settings/tokens

REPO_OWNER="kghatak"
REPO_NAME="iomrscanner"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable not set"
    echo ""
    echo "To use this script:"
    echo "1. Create a GitHub Personal Access Token at: https://github.com/settings/tokens"
    echo "2. Grant it 'actions:write' permission"
    echo "3. Run: export GITHUB_TOKEN='your_token_here'"
    echo "4. Run this script again"
    exit 1
fi

echo "🧹 Cleaning up old GitHub Actions artifacts..."
echo "Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Get all artifacts
ARTIFACTS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/artifacts?per_page=100")

# Count total artifacts
TOTAL=$(echo "$ARTIFACTS" | jq '.artifacts | length')
echo "📊 Found $TOTAL artifacts"

# Delete artifacts older than 7 days
DELETED=0
NOW=$(date +%s)

echo "$ARTIFACTS" | jq -r '.artifacts[] | "\(.id)|\(.name)|\(.created_at)"' | while IFS='|' read -r id name created_at; do
    CREATED=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$created_at" +%s 2>/dev/null || date -d "$created_at" +%s 2>/dev/null)
    AGE_DAYS=$(( (NOW - CREATED) / 86400 ))
    
    if [ $AGE_DAYS -gt 7 ]; then
        echo "🗑️  Deleting: $name (${AGE_DAYS} days old, ID: $id)"
        curl -s -X DELETE \
            -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/artifacts/$id" > /dev/null
        DELETED=$((DELETED + 1))
    fi
done

echo ""
echo "✅ Cleanup complete! Deleted artifacts older than 7 days."
echo ""
echo "💡 Tip: The workflow has been updated to automatically clean up artifacts."
echo "   Artifacts are now retained for only 7 days and compressed to save space."

