AUTOMORPH — dataset exports and reproducibility notes

Overview
--------
This folder contains image- and participant-level CSVs produced by the AUTOMORPH pipeline for the Retfound experiments. Files were generated from:
- vessel_features_merged.csv (image-level vessel features)
- retina_ckd_survival_ready_PAIRED.csv (participant table with left/right file names and eid)

This README documents which files to use, how they were created, counts, and exact commands to reproduce the outputs locally.

Primary files (one-row-per-participant)
---------------------------------------
- master_participant_level_single_image_aggregated.csv
  - Description: One row per participant. For each numeric feature, value is taken from the left-eye measurement when available; otherwise the right-eye measurement is used (left-preferred, right-fallback). Column names are base feature names (no _left/_right suffix). Use this for training Retfound models that expect exactly one row per participant.
  - Path: M:/NEW-PROJECT/AUTOMORPH/master_participant_level_single_image_aggregated.csv

- master_participant_level_single_image.csv
  - Description: Full participant table with metadata and the merged left_/right_ columns as well as the combined base-named features.
  - Path: M:/NEW-PROJECT/AUTOMORPH/master_participant_level_single_image.csv

Provenance / eye provenance
---------------------------
- master_participant_eye_used.csv — lists per `eid` which eye contributed the features in the combined single-image file.
  - Values: 'left' or 'right'
  - Path: M:/NEW-PROJECT/AUTOMORPH/master_participant_eye_used.csv

Left-only and right-only experiment files
----------------------------------------
- master_participant_level_left_only_aggregated.csv  (left-only aggregated)
- master_participant_level_left_only.csv             (left-only full)
- master_participant_level_right_only_aggregated.csv (right-only aggregated)
- master_participant_level_right_only.csv            (right-only full)

Image-level and QC
------------------
- master_image_level.csv — image-level rows, mapping info and mapping_status for each image row.
- qc_report.txt — run counts and quick QC summary.
- participants_only_right.csv — list of eids that only had right-image matches (useful for auditing)

Counts (from most recent run)
-----------------------------
- Total participants in `pat` (retina_ckd_survival_ready_PAIRED.csv): 85,333
- Participants with at least one mapped image (left or right): 16,458
  - only left: 6,502
  - only right: 8,212
  - both left and right: 1,744
- Left-only exported participants: 8,246
- Right-only exported participants: 8,212
- Combined (left preferred, right fallback): 16,458
- Image-level rows in vessel_features_merged.csv: 31,389

Notes on how features were merged
---------------------------------
- Feature selection: only numeric columns from `vessel_features_merged.csv` were treated as features. Non-numeric columns and mapping columns were excluded from aggregation.
- Combined logic: for each numeric feature f, code sets final feature f = left_f (if present) else right_f. The `eye_used` column indicates the source.
- Left-only and right-only CSVs were created by filtering based on `eye_used` / `used_left` / `used_right` flags.

Reproducibility — run locally
----------------------------
Prerequisites:
- Python (tested with the conda environment used here)
- pandas, numpy installed in the environment
- Files present in M:/NEW-PROJECT/AUTOMORPH: vessel_features_merged.csv and retina_ckd_survival_ready_PAIRED.csv

Run steps (PowerShell example using a conda/python path):

# Use the conda env you used during development (example)
& 'D:\conda_envs\new_env\python.exe' "M:\NEW-PROJECT\AUTOMORPH\Creating new image and participant level QC.py"

This will (re)generate:
- master_image_level.csv
- master_participant_level_single_image.csv
- master_participant_level_single_image_aggregated.csv
- master_participant_eye_used.csv
- qc_report.txt

To export left-only or right-only CSVs run:
& 'D:\conda_envs\new_env\python.exe' "M:\NEW-PROJECT\AUTOMORPH\export_left_only.py"
& 'D:\conda_envs\new_env\python.exe' "M:\NEW-PROJECT\AUTOMORPH\export_right_only.py"

Suggested experiments
---------------------
- Baseline: use `master_participant_level_left_only_aggregated.csv` to train with left-eye features only (no cross-eye leakage). 8,246 participants.
- Combined: use `master_participant_level_single_image_aggregated.csv` (left preferred, right fallback) to maximize sample size (16,458 participants). Include `eye_used` or `used_right` as a covariate to control for eye differences.
- Two-eye model: use `master_participant_level_single_image.csv` (contains `left_` and `right_` columns) so models can explicitly use both-eye measurements where available.
- Per-image model: use `master_image_level.csv` to build an image-level model (two rows per participant) — take care with cross-validation (prevent same participant in both train/test folds).

Caveats and recommendations
---------------------------
- To avoid leakage when doing k-fold cross-validation, ensure participant-level splitting (not image-level) if you use both-eye data or per-image data. Do not place the two images from the same participant across train/test folds.
- The combined dataset selects left-first. If you later want to treat right-only participants differently, keep `master_participant_eye_used.csv` and `used_right` flags to stratify or use as covariates.

Packaging for GitHub
--------------------
- Recommended: commit this README and the small scripts (Creating new image and participant level QC.py, export_left_only.py, export_right_only.py) to the repo. Do NOT commit large CSVs to the repo — instead export the CSVs to a release asset or store them on a data server and include download instructions.

If you want, I can:
- Add a small README section that includes the exact git commands to add/commit these scripts and the README.
- Produce a compressed archive (.zip) of the aggregated CSVs ready for upload.

Contact / notes
---------------
If you want me to also add a short Jupyter notebook comparing distributions of a few key features across left/right/combined, I can add that next (it will include simple plots and summary statistics).

GitHub: add scripts to your existing repo (example PowerShell commands)
---------------------------------------------------------------
Run these from PowerShell inside M:\NEW-PROJECT\AUTOMORPH (or adjust the paths). These commands will add the scripts and README to your repository while ignoring CSVs via .gitignore.

cd 'M:\NEW-PROJECT\AUTOMORPH'

# Initialize git and add remote (skip if the repo is already set up)
git init
git remote add origin https://github.com/Effendy77/retina-renal-ai.git

# Stage scripts and README (note: the long filename with spaces is escaped by quoting)
git add "Creating new image and participant level QC.py" export_left_only.py export_right_only.py count_right_drops.py verify_left_right_separate_images.py README.md .gitignore

# Commit and push (adjust branch name if needed)
git commit -m "Add AUTOMORPH preprocessing scripts and README (left/right export, QC)"
git branch -M main
git push -u origin main

Notes:
- If your GitHub repo already has commits, prefer to `git pull` first or create a branch to avoid overwriting history.
- CSVs are excluded by .gitignore; if you need to force-add a small CSV, use `git add -f <file>` selectively.
