# Tabbed Review Tool - Visual Guide

## 🎯 New Three-Tab Interface

The manual review tool now has **three confidence-based tabs** for faster, more focused review!

---

## 📑 Tab Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  🔴 Low Confidence (<50%)  │ 🟡 Medium (50-90%) │ 🟢 High (>90%) │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Scrollable Table with:                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Patch | Col | Q | Opt | Conf | Fill | Initial | Reviewed │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ col1_q01_a | 1 | 1 | a | 0.35 | 0.25 | unmarked | marked │  │ ← Changed: GREEN BG
│  │ col1_q01_b | 1 | 1 | b | 0.42 | 0.78 | marked | marked   │  │ ← Same: Normal
│  │ col1_q01_c | 1 | 1 | c | 0.45 | 0.12 | unmarked |(pending)│  │ ← Not reviewed
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Mark] [Unmark] buttons for each row                          │
│  Preview image (3× zoom) shown in last column                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Color Coding

### Tab Colors
- **🔴 Red Tab**: Low confidence (<50%) - **REVIEW FIRST!**
- **🟡 Yellow Tab**: Medium confidence (50-90%) - Quick check
- **🟢 Green Tab**: High confidence (>90%) - Usually correct

### Row Highlighting
- **🟢 GREEN BACKGROUND**: Label changed from initial (your correction applied)
- **White/Gray alternating**: Standard rows (unchanged or same as initial)

### Cell Colors
- **Fill Ratio:**
  - Green: >0.4 (likely marked)
  - Yellow: 0.2-0.4 (ambiguous)
  - Gray: <0.2 (likely unmarked)

### Text Colors
- **Dark green text**: 'marked' label
- **Gray text**: 'unmarked' label
- **Black text**: Changed labels (on green background)

---

## 🚀 Quick Start

```bash
source venv/bin/activate
python tools/manual_review_tool.py
```

### Interface Layout:

```
┌────────────────────────────────────────────────────────────────┐
│ [📁 Load Dataset] [💾 Save Changes] [✅ Bulk Approve All]     │
├────────────────────────────────────────────────────────────────┤
│ Loaded 400 patches                                             │
├────────────────────────────────────────────────────────────────┤
│ 📊 Total: 400 | Reviewed: 150 | Pending: 250 | Changed: 23    │
├────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 🔴 Low (<50%): 45  │ 🟡 Med (50-90%): 155 │ 🟢 High: 200 │  │
│ ├──────────────────────────────────────────────────────────┤  │
│ │                                                           │  │
│ │  [Scrollable table with all patches in current tab]      │  │
│ │                                                           │  │
│ │  Each row: Patch info | Buttons | Preview image          │  │
│ │                                                           │  │
│ └──────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│ 💡 Instructions: Click Mark/Unmark buttons...                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 📋 Workflow by Tab

### Tab 1: 🔴 Low Confidence (<50%) - CRITICAL

**Contains:** Ambiguous circles that need human judgment

**Typical count:** 40-80 patches (10-20% of total)

**Action:**
1. **Review EVERY row** carefully
2. Look at preview image
3. Check fill_ratio
4. Click Mark or Unmark
5. **Changed rows turn GREEN**

**Time:** 5-10 minutes for 50 patches

---

### Tab 2: 🟡 Medium Confidence (50-90%) - QUICK CHECK

**Contains:** Probably correct, but worth checking

**Typical count:** 150-200 patches (40-50% of total)

**Action:**
1. **Scroll through quickly**
2. Spot-check random rows
3. Correct only obvious mistakes
4. Most can be left as-is

**Time:** 3-5 minutes for 150 patches

---

### Tab 3: 🟢 High Confidence (>90%) - SPOT CHECK

**Contains:** Very confident predictions

**Typical count:** 150-250 patches (40-60% of total)

**Action:**
1. **Quick scroll** to see if anything looks wrong
2. Usually all correct
3. Can skip entirely if confident in ML
4. Or just check first/last 10 rows

**Time:** 1-2 minutes for 200 patches

---

## ⚡ Review Strategies

### Strategy 1: Thorough Review (15-20 minutes)
```
1. Tab 1 (Low): Review ALL rows individually
2. Tab 2 (Medium): Review 50% of rows (sample)
3. Tab 3 (High): Review first/last 20 rows
4. Save changes
```
**Best for:** First dataset, establishing baseline quality

---

### Strategy 2: Quick Review (5-10 minutes)
```
1. Tab 1 (Low): Review ALL rows
2. Tab 2 (Medium): Scroll, check random 20 rows
3. Tab 3 (High): Skip entirely
4. Click "Bulk Approve All" for unchecked rows
5. Save changes
```
**Best for:** Good quality scans, trust ML mostly

---

### Strategy 3: Ultra-Fast (2-5 minutes)
```
1. Tab 1 (Low): Review ALL rows (most critical)
2. Click "Bulk Approve All" for tabs 2 & 3
3. Save changes
```
**Best for:** High-quality data, time-constrained

---

### Strategy 4: Lazy Approve (1 minute)
```
1. Click "Bulk Approve All"
2. Quick scroll Tab 1 to see if anything obviously wrong
3. Save changes
```
**Best for:** Trust traditional classifier completely (85-92% accuracy)

---

## 🎨 Visual Indicators

### In the Table:

**Green Background Row:**
```
col1_q05_b | 1 | 5 | b | 0.42 | 0.18 | marked | unmarked | [Buttons] | [Image]
                                       ^^^^^^   ^^^^^^^^^^
                                       Initial  Reviewed (DIFFERENT → GREEN)
```

**Normal Row (Same as Initial):**
```
col1_q05_c | 1 | 5 | c | 0.95 | 0.75 | marked | marked | [Buttons] | [Image]
                                       ^^^^^^   ^^^^^^
                                       Initial  Reviewed (SAME → Normal color)
```

**Pending Row (Not Reviewed):**
```
col1_q05_d | 1 | 5 | d | 0.88 | 0.12 | unmarked | (pending) | [Buttons] | [Image]
                                                   ^^^^^^^^^
                                                   Not reviewed yet
```

---

## 📊 Statistics Bar Explanation

```
📊 Total: 400 | ✅ Reviewed: 150 (37.5%) | ⏳ Pending: 250 | 
   🔄 Changed: 23 | 🟢 Marked: 80 | ⚪ Unmarked: 70 || 
   Tabs: 🔴 45 | 🟡 155 | 🟢 200
```

- **Total**: All patches in dataset
- **Reviewed**: Have reviewed_label set
- **Pending**: Still need review (reviewed_label empty)
- **Changed**: Labels different from initial (green rows)
- **Marked/Unmarked**: Count of reviewed labels
- **Tabs**: Count in each confidence tab

---

## 💡 Pro Tips

### Tip 1: Start with Red Tab
Always review **🔴 Low Confidence** tab first:
- These are the most uncertain
- Most likely to have errors
- Usually only 40-80 patches
- Takes 5-10 minutes

### Tip 2: Bulk Approve High Confidence
If High Confidence tab looks good:
- Sample 20-30 rows
- If all correct → Click "Bulk Approve All"
- Saves tons of time!

### Tip 3: Watch for Green Highlighting
Green background = you changed it from ML prediction:
- Good for tracking your corrections
- Easy to see where you disagreed with ML
- Helps identify ML weaknesses

### Tip 4: Use Fill Ratio as Guide
- **>0.5**: Almost certainly marked
- **<0.15**: Almost certainly unmarked
- **0.15-0.35**: Check the preview image carefully

### Tip 5: Save Frequently
Click "Save All Changes" every 50-100 reviews

---

## 🔍 Common Patterns to Watch For

### Pattern 1: Student Marked Multiple Answers
```
Row 1: a=marked, b=unmarked, c=unmarked, d=unmarked ✅
Row 2: a=marked, b=marked, c=unmarked, d=unmarked   ⚠️ Two marked!
```
**Action:** Check if both are really marked or ML error

### Pattern 2: All Same Answer
```
Q1: b=marked
Q2: b=marked
Q3: b=marked
...all 'b' options marked
```
**Action:** Verify if student really chose 'b' for all

### Pattern 3: Stray Marks
```
Preview shows: Pencil mark NEAR circle but not IN circle
Initial: marked (wrong!)
```
**Action:** Click "Unmark" → Row turns GREEN

### Pattern 4: Light Marks
```
Fill ratio: 0.25 (borderline)
Preview: Very faint mark inside
```
**Action:** Your judgment - usually "Mark"

---

## ⌨️ Keyboard Shortcuts (Future Enhancement)

Not yet implemented, but planned:
- `1` - Mark current row
- `2` - Unmark current row
- `↓` - Next row
- `↑` - Previous row
- `Tab` - Next confidence tab
- `Ctrl+S` - Save changes

---

## ✅ Complete Review Checklist

- [ ] Load dataset
- [ ] Review **ALL** red tab (low confidence) patches
- [ ] Spot-check yellow tab (medium confidence)
- [ ] Sample green tab (high confidence)
- [ ] Check statistics (reasonable marked/unmarked ratio?)
- [ ] Save changes
- [ ] Verify metadata.csv updated

**Then proceed to training!**

---

## 🎉 Benefits of Tabbed Interface

| Feature | Old Tool | New Tool |
|---------|----------|----------|
| View mode | One-by-one | All visible in table |
| Navigation | Arrow keys | Scroll + tabs |
| Sorting | None | By confidence |
| Tabs | Single view | 3 tabs by confidence |
| Changed tracking | None | ✅ Green highlighting |
| Bulk operations | None | ✅ Bulk approve |
| Review time (400) | 30-60 min | 5-15 min |
| Efficiency | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📈 Expected Outcomes

### After reviewing 400 patches:
- **High confidence (>90%)**: 98-99% correct after review
- **Medium confidence (50-90%)**: 95-97% correct after review
- **Low confidence (<50%)**: 90-95% correct after review

### Training results with reviewed data:
- **Model accuracy**: 96-98% (vs 93-95% without review)
- **Confidence**: Better calibrated
- **Edge cases**: Handles better

**The tabbed interface makes high-quality dataset creation fast and efficient!** 🚀

