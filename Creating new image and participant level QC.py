# Requirements: pandas, numpy
import pandas as pd
import numpy as np
import os

# 1. Load CSVs
vessel = pd.read_csv("M:/NEW-PROJECT/AUTOMORPH/vessel_features_merged.csv", low_memory=False)
pat = pd.read_csv("M:/NEW-PROJECT/AUTOMORPH/retina_ckd_survival_ready_PAIRED.csv", low_memory=False)
# Output directory (change here if you want outputs elsewhere)
OUTPUT_DIR = r"M:/NEW-PROJECT/AUTOMORPH"

# 2. Normalize filenames: extract basename, strip whitespace and lower
def norm_fname(x):
    if pd.isna(x): 
        return np.nan
    x = str(x).strip()
    x = os.path.basename(x)   # removes any path
    x = x.lower()
    return x

vessel["orig_fname_norm"] = vessel["original_filename"].apply(norm_fname)

# If vessel has file extension variations or extra suffixes, you can optionally remove extensions:
vessel["orig_fname_stem"] = vessel["orig_fname_norm"].str.replace(r'\.[a-z0-9]+$', '', regex=True)

pat["left_fname_norm"] = pat["left_image_filename"].apply(norm_fname)
pat["left_fname_stem"] = pat["left_fname_norm"].str.replace(r'\.[a-z0-9]+$', '', regex=True)
pat["right_fname_norm"] = pat["right_image_filename"].apply(norm_fname)
pat["right_fname_stem"] = pat["right_fname_norm"].str.replace(r'\.[a-z0-9]+$', '', regex=True)

# 3. Image-level merge: attach eid to vessel rows by matching on filename stem first, then full name as fallback

# Create mapping table: filename stem -> set of eids (in case duplicates exist)
left_map = pat[["eid", "left_fname_norm", "left_fname_stem"]].dropna(subset=["left_fname_stem"]).rename(
    columns={"left_fname_stem": "fname_stem", "left_fname_norm": "fname_norm"})
right_map = pat[["eid", "right_fname_norm", "right_fname_stem"]].dropna(subset=["right_fname_stem"]).rename(
    columns={"right_fname_stem": "fname_stem", "right_fname_norm": "fname_norm"})
maps = pd.concat([left_map, right_map], ignore_index=True)
maps = maps.drop_duplicates(subset=["eid", "fname_stem", "fname_norm"])

# If multiple eids map to same filename, we'll flag it for QC
fname_to_eids = maps.groupby("fname_stem")["eid"].unique().to_dict()

def map_eid_by_stem(stem):
    if pd.isna(stem):
        return np.nan
    eids = fname_to_eids.get(stem)
    if isinstance(eids, (list, np.ndarray)) and len(eids) == 1:
        return eids[0]
    # ambiguous or not found
    return np.nan

vessel["matched_eid_stem"] = vessel["orig_fname_stem"].apply(map_eid_by_stem)

# For those unmatched by stem, try matching by full normalized filename
fname_norm_to_eids = maps.groupby("fname_norm")["eid"].unique().to_dict()

def map_eid_by_full_norm(fname):
    if pd.isna(fname):
        return np.nan
    eids = fname_norm_to_eids.get(fname)
    if isinstance(eids, (list, np.ndarray)) and len(eids) == 1:
        return eids[0]
    return np.nan

vessel["matched_eid_full"] = vessel["orig_fname_norm"].apply(map_eid_by_full_norm)

# Prefer stem match then full match
vessel["eid"] = vessel["matched_eid_stem"].combine_first(vessel["matched_eid_full"])

# Keep track of mapping status
def mapping_status(row):
    if not pd.isna(row["matched_eid_stem"]): return "stem_matched"
    if not pd.isna(row["matched_eid_full"]): return "full_matched"
    return "unmatched"

vessel["mapping_status"] = vessel.apply(mapping_status, axis=1)

# 4. Save image-level master
vessel.to_csv(os.path.join(OUTPUT_DIR, "master_image_level.csv"), index=False)

# 5. Participant-level left/right pivot: join vessel features into participant table

# Prepare vessel features: select numeric feature columns only (exclude mapping/meta columns)
exclude = {"original_filename", "orig_fname_norm", "orig_fname_stem", "matched_eid_stem", "matched_eid_full", "eid", "mapping_status"}
# Prefer numeric columns only to avoid aggregation errors on string columns
numeric_cols = vessel.select_dtypes(include=[np.number]).columns.tolist()
feature_cols = [c for c in numeric_cols if c not in exclude]

# Split vessel into left/right by matching to participants using left/right normalized filename
# Merge left features
left = vessel.merge(pat[["eid", "left_fname_stem"]], left_on="orig_fname_stem", right_on="left_fname_stem", how="inner", suffixes=("","_pat"))
left = left.rename(columns={c: f"left_{c}" for c in feature_cols if c in left.columns})
# Keep only eid and left_* features
left_cols_keep = ["eid"] + [c for c in left.columns if c.startswith("left_")]
left = left[left_cols_keep].drop_duplicates(subset=["eid"])

# Also merge right-eye features so we can build a combined single-image per participant (left preferred, otherwise right)
right = vessel.merge(pat[["eid", "right_fname_stem"]], left_on="orig_fname_stem", right_on="right_fname_stem", how="inner", suffixes=("","_pat"))
right = right.rename(columns={c: f"right_{c}" for c in feature_cols if c in right.columns})
# Keep only eid and right_* features
right_cols_keep = ["eid"] + [c for c in right.columns if c.startswith("right_")]
right = right[right_cols_keep].drop_duplicates(subset=["eid"])

# Combine left/right into participant table
participant = pat.copy()
participant = participant.merge(left, on="eid", how="left")
participant = participant.merge(right, on="eid", how="left")

# 6. QC flags and aggregations
# Coerce any left_/right_ merged columns to numeric (invalid parsing -> NaN) before aggregation
for c in participant.columns:
    if c.startswith("left_") or c.startswith("right_"):
        participant[c] = pd.to_numeric(participant[c], errors='coerce')

participant["has_left_features"] = participant[[c for c in participant.columns if c.startswith("left_")]].notna().any(axis=1)
participant["has_right_features"] = participant[[c for c in participant.columns if c.startswith("right_")]].notna().any(axis=1)
participant["num_images_with_features"] = participant[["has_left_features","has_right_features"]].sum(axis=1)
# number of images with left-eye features specifically (useful for QC/selection)
participant["num_images_with_left_eye_features"] = participant["has_left_features"].astype(int)

# Build combined single-image features: prefer left if present, otherwise use right. Record which eye was used.
# initialize as object dtype to avoid dtype issues when assigning string labels
participant["eye_used"] = pd.Series([None] * len(participant), dtype=object)
for f in feature_cols:
    left_col = f"left_{f}"
    right_col = f"right_{f}"
    # create combined base feature name (overwrite if exists)
    if left_col in participant.columns or right_col in participant.columns:
        # where left present use left, else use right
        vals = None
        if left_col in participant.columns and right_col in participant.columns:
            vals = participant[left_col].combine_first(participant[right_col])
        elif left_col in participant.columns:
            vals = participant[left_col]
        else:
            vals = participant[right_col]
        participant[f] = vals

# Determine eye_used: left if any left feature present, else right if any right feature present
participant.loc[participant[ [c for c in participant.columns if c.startswith('left_')] ].notna().any(axis=1), 'eye_used'] = 'left'
participant.loc[(participant['eye_used'].isna()) & (participant[ [c for c in participant.columns if c.startswith('right_')] ].notna().any(axis=1)), 'eye_used'] = 'right'

# Also create simple flags for QC
participant['used_left'] = participant['eye_used'] == 'left'
participant['used_right'] = participant['eye_used'] == 'right'


# 7. Basic QC report counts
qc = {}
qc["n_vessel_rows"] = len(vessel)
qc["n_unique_image_filenames_in_vessel"] = vessel["orig_fname_stem"].nunique()
qc["n_pat_rows"] = len(pat)
qc["n_left_fnames_nonmissing"] = pat["left_fname_stem"].notna().sum()
# Right-eye counts removed intentionally; pipeline uses left eye only
qc["n_images_mapped_to_eid"] = vessel["eid"].notna().sum()
qc["n_unique_eids_mapped_from_images"] = vessel["eid"].dropna().nunique()
qc["n_participants_with_left_eye_features"] = participant["has_left_features"].sum()
qc["n_participants_with_right_eye_features"] = participant["has_right_features"].sum()
qc["n_participants_used_left"] = participant['used_left'].sum()
qc["n_participants_used_right"] = participant['used_right'].sum()

with open("qc_report.txt", "w") as fh:
    for k,v in qc.items():
        fh.write(f"{k}: {v}\n")

# 8. Save participant-level outputs (single-image per participant: left eye only)
participant.to_csv(os.path.join(OUTPUT_DIR, "master_participant_level_single_image.csv"), index=False)

# Save aggregated participant summary (select only eid, key covariates, and aggregated features)
# Also provide aggregated participant summary with base feature names (no suffix) so downstream expects one image per participant
# Copy left-prefixed feature columns into base feature names (overwrite if present)
for f in feature_cols:
    left_col = f"left_{f}"
    if left_col in participant.columns:
        participant[f] = participant[left_col]

agg_cols = ["eid", "num_images_with_left_eye_features", "has_left_features"]
agg_cols += [f for f in feature_cols if f in participant.columns]
participant[agg_cols].to_csv(os.path.join(OUTPUT_DIR, "master_participant_level_single_image_aggregated.csv"), index=False)

# Also save a file indicating which eye was used per participant
participant[['eid','eye_used']].to_csv(os.path.join(OUTPUT_DIR, 'master_participant_eye_used.csv'), index=False)

# 9. Print a brief summary to console
print(f"Saved: {os.path.join(OUTPUT_DIR, 'master_image_level.csv')}, {os.path.join(OUTPUT_DIR, 'master_participant_level_single_image.csv')}, {os.path.join(OUTPUT_DIR, 'master_participant_level_single_image_aggregated.csv')}, {os.path.join(OUTPUT_DIR, 'master_participant_eye_used.csv')}, {os.path.join(OUTPUT_DIR, 'qc_report.txt')}")
print(qc)
