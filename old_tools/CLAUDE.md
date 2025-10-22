# OLD TOOLS (DEPRECATED)

## Purpose
Archive of experimental, deprecated, and no-longer-used tools. Kept for historical reference and potential code reuse.

## ⚠️ WARNING
**These tools are NOT actively maintained and may not work with current project structure.**
**Use active tools in `../labeling_tools/`, `../utilities/`, `../training_tools/`, or `../testing_tools/` instead.**

---

## PDF Labeling Tools (Experimental)

These tools were experiments for labeling PDF-extracted images. The project moved away from PDF processing to direct image labeling.

### simple_pdf_labeler.py
- **Purpose:** Basic PDF image labeling attempt
- **Status:** Superseded by web annotation tool
- **Issues:** Limited zoom, poor UX for large images

### improved_pdf_labeler.py
- **Purpose:** Enhanced PDF labeler with zoom functionality
- **Status:** Better than simple version, but still not production-ready
- **Features:** Zoom, pan, better image handling
- **Why Deprecated:** tkinter limitations for professional workflow

### robust_pdf_labeler.py
- **Purpose:** More stable PDF labeling tool
- **Status:** Attempted to fix crashes and improve stability
- **Why Deprecated:** Still had performance issues with large images

### fullpage_labeler.py
- **Purpose:** Full-page PDF labeling interface
- **Status:** Tried to handle entire page view
- **Why Deprecated:** Difficult to annotate small objects on full page

### ultra_simple_labeler.py
- **Purpose:** Minimalist labeling interface
- **Status:** Stripped down for speed
- **Why Deprecated:** Too minimal, lacking essential features

### click_delete_labeler.py
- **Purpose:** Alternative interface with click-to-delete
- **Status:** Experimental UI pattern
- **Why Deprecated:** Awkward workflow, not intuitive

**Replacement:** Use `../labeling_tools/annotation_tool/` (modern web interface)

---

## PDF Processing Utilities

### pdf_to_images.py
- **Purpose:** Extract images from PDF documents
- **Status:** Functional but no longer needed
- **Why Deprecated:** Project shifted to direct image input

### prepare_pdf_data.py
- **Purpose:** Organize PDF-extracted images for labeling
- **Status:** Worked for PDF workflow
- **Why Deprecated:** No longer processing PDFs

**Note:** If PDF processing is needed again, these scripts can be revived

---

## One-Time Utilities

### modify_class_names.py
- **Purpose:** Changed class names in trained model
- **Status:** Successfully updated model from v1 to v2 class names
- **Result:** Created `best_v2_updated_classes.pt`
- **Usage:** ONE-TIME script - already executed
- **When Used:** September 2025 to update class nomenclature
- **Output:** Modified model in `../models/`

**Warning:** Don't run again unless intentionally modifying model classes

### verify_model_changes.py
- **Purpose:** Verify that model class changes were applied correctly
- **Status:** Validation script for modify_class_names.py
- **Usage:** ONE-TIME verification
- **Result:** Confirmed v2 model has updated class names

**Note:** Historical verification tool, not needed for regular workflow

---

## Miscellaneous

### navigation_fix.js
- **Purpose:** JavaScript fix for web interface navigation
- **Status:** Experimental fix, may have been integrated or abandoned
- **Context:** Early web tool development
- **Why Here:** Not part of final web tool implementation

---

## Why These Tools Were Deprecated

### PDF Labeling Tools
1. **Performance Issues:** tkinter struggled with large PDF images
2. **Poor UX:** Zoom/pan was clunky and unintuitive
3. **Better Alternative:** Modern web tool (`annotation_tool/`) provides superior experience
4. **Workflow Change:** Project moved to direct image labeling, not PDF extraction

### One-Time Scripts
1. **Task Completed:** modify_class_names.py served its purpose
2. **No Longer Needed:** Model classes are now correct
3. **Historical Value:** Kept for reference if similar changes needed

### Experimental Tools
1. **Failed Experiments:** Some interface patterns didn't work well
2. **Better Solutions Found:** Active tools provide better workflows
3. **Learning Process:** Valuable for understanding what NOT to do

---

## Potential Reuse

### If PDF Processing Needed Again
- `pdf_to_images.py` - Still functional for PDF extraction
- `prepare_pdf_data.py` - Can organize PDF-derived images

### If Modifying Model Classes Again
- `modify_class_names.py` - Template for model modification
- `verify_model_changes.py` - Validation approach

### Code Snippets
- PDF labeling tools have useful code for:
  - Image zoom/pan in tkinter
  - PDF handling with PyMuPDF
  - Large image memory management

---

## Active Tool Alternatives

| Old Tool | Use Instead |
|----------|-------------|
| simple_pdf_labeler.py | ../labeling_tools/annotation_tool/ |
| improved_pdf_labeler.py | ../labeling_tools/annotation_tool/ |
| robust_pdf_labeler.py | ../labeling_tools/annotation_tool/ |
| fullpage_labeler.py | ../labeling_tools/annotation_tool/ |
| ultra_simple_labeler.py | ../labeling_tools/label_tool.py |
| click_delete_labeler.py | ../labeling_tools/enhanced_label_tool.py |
| pdf_to_images.py | Direct image input (no PDF) |
| prepare_pdf_data.py | ../utilities/create_training_dataset.py |

---

## Maintenance Policy

### These Tools Are:
- ❌ NOT maintained or updated
- ❌ NOT tested with current project structure
- ❌ NOT recommended for active use
- ✅ Kept for historical reference
- ✅ Available for code reference
- ✅ Could be revived if specific need arises

### If You Need to Use Something Here:
1. **First:** Check if active tools can do the job
2. **Second:** Check if tool still runs with current setup
3. **Third:** Update paths and dependencies
4. **Document:** Why you're using deprecated tool
5. **Consider:** Modernizing or porting to active tools

---

## Cleanup Considerations

### Can Be Deleted If:
- Confirmed never needed again
- Disk space is critical
- Project is stable and deployed
- Historical reference no longer valuable

### Should Keep If:
- Uncertainty about future PDF processing needs
- Learning from past experiments valuable
- Code snippets might be useful
- Minimal disk space impact

**Current Recommendation:** Keep archived, low maintenance overhead

---

## Dependencies

If you need to run any of these:

```bash
pip install opencv-python Pillow tkinter PyMuPDF torch ultralytics
```

**Note:** May require additional dependencies depending on specific tool

---

## Historical Context

**PDF Era (Early September 2025):**
- Initial approach: Extract images from PDFs → Label → Train
- Problem: PDFs varied in quality, extraction was inconsistent
- Result: Multiple labeling tool iterations trying to fix issues

**Pivot (Mid-September 2025):**
- Shifted to direct image input
- Developed modern web annotation tool
- Achieved better workflow and user experience

**Model Update (Late September 2025):**
- Used modify_class_names.py to update class nomenclature
- Verified changes with verify_model_changes.py
- Successfully deployed v2 model

**Reorganization (October 2025):**
- Moved experimental tools to old_tools/
- Established clear active vs deprecated separation
- Documented reasons for deprecation

---

## Learning Points

### What Worked:
- Rapid experimentation led to better understanding
- Iterative improvement of interfaces
- Clean pivot when approach wasn't working

### What Didn't Work:
- Over-reliance on tkinter for complex UI
- PDF processing added unnecessary complexity
- Too many similar tools instead of one good one

### Lessons Applied:
- Modern web tools for professional interfaces
- Focus on one excellent tool vs many mediocre tools
- Direct approach (images) vs indirect (PDFs)

---

## Questions?

If you're considering using anything from old_tools/:

1. **Ask:** Why not use active tools?
2. **Check:** Does it still work with current setup?
3. **Document:** Your use case and findings
4. **Consider:** Contributing improvements to active tools instead

For most use cases, active tools are the better choice.
