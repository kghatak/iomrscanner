# Manual Review Tool - Table View Guide

## 🎯 New Features

### ✅ What Changed

**OLD Tool (One-by-one):**
- ❌ Shows one image at a time
- ❌ Slow navigation
- ❌ Hard to see patterns
- ❌ No bulk operations

**NEW Tool (Table View):**
- ✅ **Scrollable table** showing all patches at once
- ✅ **Sorted by confidence** (low confidence first - review critical ones)
- ✅ **Visual preview** in each row
- ✅ **Quick buttons** to mark/unmark
- ✅ **Bulk approve** entire dataset
- ✅ **Color-coded** confidence and labels
- ✅ **Track changes** with yellow highlighting

---

## 🚀 How to Use

### Step 1: Launch the Tool

```bash
source venv/bin/activate
python tools/manual_review_tool.py
```

### Step 2: Load Dataset

Click **"📁 Load Dataset Directory"** and select your dataset folder (e.g., `page_1_ml_dataset`)

The tool will:
- Load all 400 patches
- Sort by confidence (LOW → HIGH)
- Display in scrollable table

### Step 3: Review Patches

The table shows 10 columns:

| Column | What It Shows | Purpose |
|--------|---------------|---------|
| **Patch** | Filename | Identifies the circle |
| **Col** | Column (1-4) | Which OMR column |
| **Q** | Question (1-25) | Which question row |
| **Opt** | Option (a-d) | Which answer option |
| **Confidence** | 0.0-1.0 | 🔴 Red: <0.7, 🟡 Yellow: 0.7-0.85, 🟢 Green: >0.85 |
| **Fill Ratio** | 0.0-1.0 | % of dark pixels |
| **Initial Label** | marked/unmarked | Automatic classification |
| **Reviewed Label** | marked/unmarked | Your correction |
| **Action** | Buttons | Click to set label |
| **Preview** | Image | 3× zoomed preview |

### Step 4: Review Low Confidence Items First

The table is **automatically sorted** with lowest confidence at the top.

**Focus on:**
- 🔴 **Red confidence** (<0.7) - Check these carefully
- 🟡 **Yellow confidence** (0.7-0.85) - Quick review
- 🟢 **Green confidence** (>0.85) - Usually correct, skip if you want

### Step 5: Set Labels

For each patch:
- Click **"Mark"** button → Sets as 'marked' (filled circle)
- Click **"Unmark"** button → Sets as 'unmarked' (empty circle)

**Changed rows turn YELLOW** so you can track your edits.

### Step 6: Bulk Approve (Optional)

If most patches look correct:
1. Review the critical low-confidence ones
2. Click **"✅ Bulk Approve All Initial Labels"**
3. All initial labels are copied to reviewed labels
4. You can still manually change individual ones after

### Step 7: Save Changes

Click **"💾 Save All Changes"** to save your reviews to `metadata.csv`

---

## 🎨 Color Coding Guide

### Confidence Colors
- 🔴 **Red** (< 0.7): Low confidence - REVIEW REQUIRED
- 🟡 **Yellow** (0.7-0.85): Medium confidence - Quick check
- 🟢 **Green** (> 0.85): High confidence - Usually correct

### Label Colors
- 🟢 **Green**: Marked (filled circle)
- ⚪ **Gray**: Unmarked (empty circle)
- 🟡 **Yellow highlight**: Row has been changed

### Row Highlighting
- **Yellow background**: You've modified this row
- **White/Gray alternating**: Unmodified rows

---

## ⚡ Quick Workflow

### For Small Datasets (100-400 patches)
```
1. Load dataset
2. Scroll through table
3. Click Mark/Unmark for any mistakes
4. Save changes
Time: 5-10 minutes
```

### For Large Datasets (1000+ patches)
```
1. Load dataset (sorted by confidence)
2. Review only LOW confidence (red rows)
3. Spot-check a few MEDIUM confidence
4. Click "Bulk Approve All"
5. Save changes
Time: 10-15 minutes
```

### Ultra-Fast Review (Trust ML)
```
1. Load dataset
2. Quick scroll to see if anything looks obviously wrong
3. Click "Bulk Approve All"
4. Save changes
Time: 1-2 minutes
```

---

## 📊 Statistics Bar

The bottom stats bar shows real-time updates:

```
📊 Total: 400 patches | ✅ Reviewed: 150 (37.5%) | ⏳ Pending: 250 | 
   🟢 Marked: 80 | ⚪ Unmarked: 70 | 🟡 Unsure: 0 || 
   Confidence: 🔴 Low(50) 🟡 Med(150) 🟢 High(200)
```

This helps you track:
- How many you've reviewed
- Distribution of labels
- Confidence distribution

---

## 💡 Pro Tips

### Tip 1: Focus on Low Confidence
Since the table is sorted by confidence, **scroll from top to bottom**:
- Top rows = Low confidence = Need review
- Bottom rows = High confidence = Usually correct

### Tip 2: Use Bulk Approve Wisely
If you see that high-confidence predictions are consistently correct:
1. Review bottom 50 rows (high confidence)
2. If all look good, bulk approve
3. Then just review the top low-confidence ones

### Tip 3: Look for Patterns
- All 'b' options marked → Student chose 'b' for all questions
- Alternating pattern → Might indicate a pattern
- Random scattered → Normal test answers

### Tip 4: Scroll Performance
For large datasets, the table loads all images. If slow:
- Review in batches of 100
- Or use filtering (future feature)

### Tip 5: Save Frequently
Click "Save All Changes" every 50-100 reviews to avoid data loss

---

## 🔍 What Each Column Tells You

### Confidence Score
- **High (>0.85)**: Clear filled or empty circle
- **Medium (0.7-0.85)**: Likely correct but review
- **Low (<0.7)**: Ambiguous - manual review needed

### Fill Ratio
- **> 0.35**: Likely marked (dark pixels)
- **< 0.15**: Likely unmarked (light pixels)
- **0.15-0.35**: Ambiguous zone

### Preview Image
- Shows 3× zoomed patch
- Should see:
  - 🔵 Blue circle outline (from normalized grid)
  - Inner filled/unfilled area
  - Letters (a, b, c, d) if visible

---

## 🎯 Common Review Scenarios

### Scenario 1: Clearly Marked
- **Preview**: Dark filled circle
- **Fill Ratio**: > 0.5
- **Confidence**: > 0.85
- **Action**: Leave as 'marked' or click "Mark" if changed

### Scenario 2: Clearly Unmarked
- **Preview**: White/light circle
- **Fill Ratio**: < 0.15
- **Confidence**: > 0.85
- **Action**: Leave as 'unmarked' or click "Unmark" if changed

### Scenario 3: Ambiguous (Needs Review)
- **Preview**: Partial fill or stray marks
- **Fill Ratio**: 0.15-0.35
- **Confidence**: < 0.7
- **Action**: Look carefully, decide marked/unmarked

### Scenario 4: Stray Mark (Not Filled)
- **Preview**: Pencil mark near but not inside circle
- **Initial**: 'marked' (wrong!)
- **Action**: Click "Unmark"

### Scenario 5: Light Mark (Barely Filled)
- **Preview**: Very light fill
- **Fill Ratio**: 0.2-0.3
- **Action**: Your judgment - usually "Mark"

---

## ⌨️ Future Enhancements (Not Yet Implemented)

Ideas for later versions:
- Filter by column/question
- Keyboard shortcuts (1=Mark, 2=Unmark)
- Show only low-confidence rows
- Undo/redo functionality
- Export statistics

---

## 📈 Expected Review Time

| Dataset Size | Quick Review | Thorough Review |
|--------------|--------------|-----------------|
| 400 patches | 5 minutes | 15 minutes |
| 1,000 patches | 10 minutes | 30 minutes |
| 5,000 patches | 30 minutes | 2 hours |
| 20,000 patches | 2 hours | 8 hours |

**Tip:** Use bulk approve + spot-check for large datasets!

---

## ✅ Workflow Summary

```
1. Launch tool: python tools/manual_review_tool.py

2. Load dataset ← Automatically sorts by confidence

3. Review critical rows (scroll from top)
   - Red confidence → Review carefully
   - Yellow confidence → Quick check
   - Green confidence → Spot check

4. Option A: Manual review
   - Click Mark/Unmark for each correction
   - Changes highlighted in yellow

   Option B: Bulk approve
   - Click "Bulk Approve All"
   - Review only mistakes after

5. Save changes ← Updates metadata.csv

6. Use for training ← python ml/train_circle_classifier.py dataset/
```

**That's it!** Fast, efficient, and thorough! 🚀

