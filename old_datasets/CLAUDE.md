# OLD DATASETS (ARCHIVED)

## Purpose
Archive of previous dataset versions, experimental data, and superseded training packages. Kept for historical reference and potential data recovery.

## ⚠️ WARNING
**These datasets are NOT current. Use `../data/` folder for active work.**
**These are archival copies that may be outdated or from experimental phases.**

---

## Active Dataset Locations

**Current Active Data:**
- `../data/unlabeled/` - New images to label
- `../data/labeled/` - Current labeled dataset
- `../data/augmented/` - Current augmented data

**Use these folders for all active work!**

---

## Archived Datasets

### old_labeld_data/
- **Original Purpose:** Initial labeled dataset output
- **Contents:** Images + YOLO labels from early labeling sessions
- **Count:** ~620 image-label pairs
- **Why Archived:** Replaced by consolidated `../data/labeled/`
- **Status:** May contain labels now in active dataset
- **Keep For:** Backup, recovery if labels lost

### old_final_labeled_dataset/
- **Original Purpose:** "Final" labeled dataset from earlier phase
- **Contents:** Full-page PDF-extracted images with labels
- **Source:** PDF labeling workflow
- **Why Archived:** Project moved away from PDF processing
- **Note:** Larger image sizes than current dataset
- **Keep For:** Historical reference, recovery if needed

### old_labeled_new_dataset/
- **Original Purpose:** "New" dataset from mid-project
- **Contents:** Labels created during dataset expansion
- **Why Archived:** Merged into current `../data/labeled/`
- **Status:** Some labels may be duplicates of active data
- **Keep For:** Verification, label comparison

### old_augmented_dataset/
- **Original Purpose:** Previous augmentation run
- **Contents:** images/ and labels/ subfolders with augmented data
- **Augmentation:** Brightness, darkening, horizontal flip
- **Why Archived:** New augmentation run created in `../data/augmented/`
- **Keep For:** Different augmentation parameters, backup

---

## PDF-Related Datasets

### old_pdf_images/
- **Original Purpose:** Images extracted from PDF documents
- **Contents:** High-resolution document page images
- **Source:** pdf_to_images.py output
- **Count:** ~100 page images
- **Why Archived:** Project pivoted away from PDF processing
- **Keep For:** Original source data, potential future PDF work

### old_pdf_labeling_data/
- **Original Purpose:** Labels for PDF-extracted images
- **Contents:** YOLO labels for PDF page images
- **Quality:** Variable (early labeling attempts)
- **Why Archived:** PDF workflow abandoned
- **Keep For:** Recovery if PDF processing returns

---

## Experimental Datasets

### old_new_dataset/
- **Original Purpose:** Experimental dataset organization
- **Contents:** Nested folder structure with images
- **Organization:** By document/page hierarchy
- **Why Archived:** Folder structure too complex
- **Status:** Flattened version created instead

### old_new_dataset_flat/
- **Original Purpose:** Flattened version of old_new_dataset
- **Contents:** All images in single level
- **Count:** ~347 images
- **Why Archived:** Data consolidated into main dataset
- **Keep For:** Backup of that batch of images

---

## Training Packages

### old_training_dataset_final/
- **Original Purpose:** Training package for model training
- **Structure:**
  ```
  train/images/, train/labels/
  val/images/, val/labels/
  dataset.yaml
  ```
- **Split:** 80/20 train/val
- **Why Archived:** New training package created with updated data
- **Keep For:** Reproduce old training runs

### old_yolo_training_dataset/
- **Original Purpose:** YOLO-formatted training package
- **Contents:** train/val split with dataset.yaml
- **Version:** Earlier dataset version
- **Why Archived:** Superseded by newer training packages
- **Keep For:** Historical training data

### old_yolo_training_dataset.zip
- **Original Purpose:** Compressed training package for Colab upload
- **Size:** 232 MB
- **Contents:** Complete training package with images and labels
- **Why Archived:** New training data available
- **Keep For:** Quick recovery of old training setup
- **Note:** Can be extracted if needed: `unzip old_yolo_training_dataset.zip`

---

## Dataset Evolution Timeline

### Phase 1: PDF Processing (Early September 2025)
- `old_pdf_images/` - Extracted from PDFs
- `old_pdf_labeling_data/` - Early labeling attempts
- **Issue:** PDF quality varied, workflow cumbersome

### Phase 2: Direct Image Labeling (Mid September 2025)
- `old_labeld_data/` - Initial direct labeling
- `old_new_dataset/` - Organized by structure
- `old_new_dataset_flat/` - Simplified structure
- **Improvement:** Cleaner workflow, better quality

### Phase 3: Consolidation (Late September 2025)
- `old_final_labeled_dataset/` - Attempted final version
- `old_labeled_new_dataset/` - Additional labels
- **Issue:** Multiple dataset copies, unclear which is current

### Phase 4: Augmentation (Late September 2025)
- `old_augmented_dataset/` - First augmentation run
- `old_training_dataset_final/` - Training package
- `old_yolo_training_dataset/` - Colab-ready package

### Phase 5: Reorganization (October 2025)
- All old datasets moved to `old_datasets/`
- Active data consolidated in `../data/`
- Clear separation between current and archived

---

## Data Relationships

```
Active Data Sources:
  ../data/unlabeled/    ← Original 310 images
  ../data/labeled/      ← Labels from consolidation of:
                          - old_labeld_data/
                          - old_labeled_new_dataset/
                          - old_final_labeled_dataset/
  ../data/augmented/    ← New augmentation run

Archived:
  old_* folders         ← Previous versions, experiments, PDF data
```

---

## Recovery Procedures

### If Current Labels Lost

1. **Check Recent Backups:**
```bash
ls -la ../data/labeled/
```

2. **Recover from Archives:**
```bash
# Copy labels from old datasets
cp old_labeld_data/*.txt ../data/labeled/
cp old_labeled_new_dataset/*.txt ../data/labeled/
```

3. **Verify Recovery:**
```bash
cd ../utilities
python dataset_stats.py
```

### If Need Old Training Setup

```bash
# Extract old training package
unzip old_yolo_training_dataset.zip -d recovered_training/

# Use for comparison or retraining
cd ../training_tools
# Edit script to point to recovered_training/dataset.yaml
```

### If PDF Data Needed

```bash
# Copy PDF images to unlabeled
cp old_pdf_images/*.png ../data/unlabeled/

# Copy labels if relabeling not needed
cp old_pdf_labeling_data/*.txt ../data/labeled/
```

---

## Disk Usage

Total archived data: ~250 MB
- Images: ~200 MB
- Labels: ~1 MB
- ZIP archive: ~232 MB
- Augmented data: ~50 MB (duplicate of originals)

**Cleanup Opportunity:** If disk space critical, can delete:
1. `old_yolo_training_dataset.zip` (extractable from folder)
2. Duplicate augmented datasets
3. Experimental datasets after verified in current data

---

## Maintenance Policy

### Keep These:
- ✅ `old_labeld_data/` - Original labels, potential recovery
- ✅ `old_final_labeled_dataset/` - Complete labeled set
- ✅ One training package ZIP for quick recovery

### Can Delete If Space Needed:
- ❌ Duplicate training packages
- ❌ Experimental organization attempts (old_new_dataset variations)
- ❌ PDF data if confirmed never returning to PDF workflow
- ❌ Multiple augmented dataset versions

### Before Deleting:
1. Verify data exists in current `../data/` folders
2. Check no unique labels in old datasets
3. Create one consolidated backup ZIP if needed
4. Document what was deleted and why

---

## Verification Checklist

Before relying solely on current data, verify:

- [ ] All labels from old_labeld_data present in ../data/labeled/
- [ ] No unique high-quality labels in old_final_labeled_dataset
- [ ] Current augmentation covers old_augmented_dataset transforms
- [ ] Training packages can be regenerated from current data
- [ ] PDF data not needed (or separately backed up)

Run verification:
```bash
# Count labels in old vs new
ls old_labeld_data/*.txt | wc -l
ls ../data/labeled/*.txt | wc -l

# Compare should show current >= old
```

---

## Usage Notes

### Accessing Old Data

```bash
# View contents
ls old_labeld_data/

# Copy specific files
cp old_labeld_data/image_001.txt ../data/labeled/

# Extract ZIP
unzip old_yolo_training_dataset.zip -d temp_extract/
```

### Comparing Versions

```bash
# Check label differences
diff old_labeld_data/image_001.txt ../data/labeled/image_001.txt

# Count total labels
grep -r "^" old_labeld_data/*.txt | wc -l
grep -r "^" ../data/labeled/*.txt | wc -l
```

---

## When to Use Old Datasets

### Good Reasons:
- Recovering accidentally deleted current data
- Comparing old vs new labels for quality assessment
- Reproducing old training results
- Investigating regression in model performance

### Bad Reasons:
- ❌ Using for new training (use current data)
- ❌ Assuming it's more complete than current (verify first)
- ❌ Avoiding reorganization work (current structure is better)

---

## Questions?

**Q: Can I delete old_datasets/?**
A: Verify current data is complete first. Then yes, if space needed.

**Q: Which dataset was used for current model?**
A: Likely combination of old_labeld_data + old_labeled_new_dataset

**Q: Should I relabel from old datasets?**
A: No, use current `../data/unlabeled/` for new work

**Q: How to consolidate everything?**
A: Current `../data/` folders already consolidate useful data

---

## Final Notes

This folder represents the evolution and experimentation that led to the current clean structure. It's valuable as:
- **Backup:** Recovery if current data issues
- **History:** Understanding project development
- **Reference:** Seeing what didn't work and why

But for active work: **Always use `../data/` folders!**
