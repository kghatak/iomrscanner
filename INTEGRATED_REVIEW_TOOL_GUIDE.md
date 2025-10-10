# Integrated Manual Review Tool - Quick Guide

## 🎯 What's New

The ML Dataset Manual Review Tool is now **integrated into the main application**!

No need to run it separately - just click a button in the main UI!

---

## 🚀 How to Access

### From Main Application Menu:

```
1. Launch main application:
   python main.py

2. Click menu: Tools → 🔍 Review ML Dataset Labels

3. Review tool opens in new window!
```

**That's it!** No separate script needed!

---

## 📋 Complete Workflow

### Step 1: Process OMR Images (Main UI)

```
1. Launch: python main.py
2. Open folder with OMR images
3. Process images (datasets auto-generated)
4. Output: image_ml_dataset/ folders created
```

### Step 2: Review Labels (Integrated Tool)

```
1. In main UI: Click Tools → Review ML Dataset Labels
2. New window opens with tabbed review interface
3. Dataset auto-loads (remembers last folder)
4. Review patches, save changes
5. Close review window when done
```

### Step 3: Train Model (Terminal)

```bash
python ml/train_circle_classifier.py path/to/dataset
```

### Step 4: Use Model (Future Integration)

```
Add MLCircleClassificationStage to pipeline
```

---

## 🎨 Menu Location

```
┌─────────────────────────────────────────────────────────┐
│ File    View    Tools    Help                           │
│                   ↓                                      │
│              ┌─────────────────────────────────────┐    │
│              │ 🔍 Review ML Dataset Labels         │    │
│              └─────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Image Panel]  │  [Results Panel]                      │
│                 │                                        │
└─────────────────────────────────────────────────────────┘
```

Click **"Tools → Review ML Dataset Labels"** to open review window.

---

## 🪟 Review Window Features

When the review tool opens, you get a **separate window** with:

### Three Tabs:
- **🔴 Low Confidence (<50%)** - Critical items first
- **🟡 Medium Confidence (50-90%)** - Quick check
- **🟢 High Confidence (>90%)** - Usually correct

### Each Tab Shows:
- Scrollable table with all patches
- Preview images (3× zoom)
- Mark/Unmark buttons
- Color-coded confidence and labels

### Top Buttons:
- **📁 Load Dataset** - Switch to different dataset
- **💾 Save Changes** - Save to metadata.csv
- **✅ Bulk Approve All** - Approve all empty cells

### Features:
- ✅ Auto-loads last dataset
- ✅ Initial labels: gray=marked, white=unmarked
- ✅ Green highlight when you change labels
- ✅ Bulk approve only fills empty cells (preserves your work!)

---

## 💡 Typical Usage Pattern

### Quick Review Session:
```
Main UI:
1. Process 5 OMR sheets → 5 datasets created

2. Click: Tools → Review ML Dataset Labels

Review Window (opens):
3. Auto-loads last dataset (e.g., page_1_ml_dataset)
4. Go to 🔴 Red tab → Review 40 patches (5 min)
5. Click "Bulk Approve All" → Fills remaining
6. Click "Save Changes"
7. Close review window

Review Window (open again):
8. Click "Load Dataset" → Select page_2_ml_dataset
9. Repeat steps 4-7
10. Review all 5 datasets in 20-30 minutes total

Main UI:
11. Continue processing more images
```

---

## 🔧 Error Handling

### If pandas not installed:

When you click **"Tools → Review ML Dataset Labels"**, you'll see:

```
⚠️ Missing Dependency

The ML Dataset Review Tool requires pandas.

To fix this issue:
1. Run: ./setup_fresh_env.sh
2. Activate: source venv/bin/activate
3. Restart the application

Error: numpy.dtype size changed...
```

**Solution:**
```bash
./setup_fresh_env.sh
source venv/bin/activate
python main.py
```

Then try again!

---

## 🎯 Advantages of Integration

### Before (Separate Script):
```bash
# Terminal 1
python main.py  # Process images

# Terminal 2  
python tools/manual_review_tool.py  # Review labels

# Need two terminals, switch between them
```

### After (Integrated):
```bash
# Single Terminal
python main.py  # Process AND review from same UI!

# Just click menu item to open review tool
# Everything in one place!
```

---

## 📊 Window Management

### Both Windows Stay Open:
- **Main Window**: Process images, view results
- **Review Window**: Review datasets, correct labels
- Work in parallel if needed
- Close review window when done
- Main window stays open

### Auto-Load Feature:
- Review window remembers last dataset
- Next time you open it → Dataset loads automatically
- No need to navigate to folder again!

---

## ✅ Complete Feature List

| Feature | Status | Location |
|---------|--------|----------|
| **Process OMR** | ✅ | Main UI |
| **Generate datasets** | ✅ | Automatic in pipeline |
| **Review labels** | ✅ | Tools menu → Opens review window |
| **Three confidence tabs** | ✅ | Review window |
| **Scrollable table** | ✅ | All tabs |
| **Green highlighting** | ✅ | Changed labels |
| **Smart bulk approve** | ✅ | Preserves manual reviews |
| **Remember folder** | ✅ | Auto-loads on open |
| **Initial label colors** | ✅ | Gray=marked, White=unmarked |
| **Train model** | ✅ | Terminal command |

---

## 🎉 Summary

**Everything is now in ONE application!**

```
┌─────────────────────────────────────────────────┐
│           Image Folder Analyzer                 │
│                                                  │
│  File   View   Tools   Help                     │
│                  ↓                               │
│         Review ML Dataset Labels ← Click here!  │
│                                                  │
│  [Process images] → [Datasets created]          │
│                                                  │
│  Then: Tools → Review → Correct labels          │
│                                                  │
│  Finally: Train model (terminal)                │
└─────────────────────────────────────────────────┘
```

**Streamlined workflow, all in one place!** 🚀

---

## 📝 Quick Reference

```bash
# 1. Fix environment (one time)
./setup_fresh_env.sh

# 2. Activate and launch
source venv/bin/activate
python main.py

# 3. In UI:
#    - Process images
#    - Tools → Review ML Dataset Labels
#    - Review and save
#    - Close review window

# 4. Train model (terminal)
python ml/train_circle_classifier.py dataset_path/
```

**That's the complete end-to-end workflow!** ✨

