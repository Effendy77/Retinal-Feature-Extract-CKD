import pandas as pd
import numpy as np
import os

vessel_fp = r"M:/NEW-PROJECT/AUTOMORPH/vessel_features_merged.csv"
pat_fp = r"M:/NEW-PROJECT/AUTOMORPH/retina_ckd_survival_ready_PAIRED.csv"

vessel = pd.read_csv(vessel_fp, low_memory=False)
pat = pd.read_csv(pat_fp, low_memory=False)

# normalize
def norm(x):
    if pd.isna(x):
        return np.nan
    x = str(x).strip()
    x = os.path.basename(x)
    x = x.lower()
    return x

vessel['stem'] = vessel['original_filename'].astype(str).map(norm).str.replace(r'\.[a-z0-9]+$','', regex=True)
pat['left_norm'] = pat['left_image_filename'].astype(str).map(norm)
pat['left_stem'] = pat['left_norm'].str.replace(r'\.[a-z0-9]+$','', regex=True)
pat['right_norm'] = pat['right_image_filename'].astype(str).map(norm)
pat['right_stem'] = pat['right_norm'].str.replace(r'\.[a-z0-9]+$','', regex=True)

left_stems = set(pat['left_stem'].dropna().unique())
right_stems = set(pat['right_stem'].dropna().unique())

# For vessel rows, determine match type
def row_type(s):
    if pd.isna(s):
        return 'none'
    left = s in left_stems
    right = s in right_stems
    if left and right:
        return 'both'
    if left:
        return 'left'
    if right:
        return 'right'
    return 'none'

vessel['match_type'] = vessel['stem'].apply(row_type)
counts = vessel['match_type'].value_counts(dropna=False).to_dict()

# Participant-level: which eids have left/right matches in vessel
# Build mapping from stem->eids for left and right (from pat)
left_map = pat[['eid','left_stem']].dropna(subset=['left_stem']).drop_duplicates()
right_map = pat[['eid','right_stem']].dropna(subset=['right_stem']).drop_duplicates()
left_map = left_map.groupby('left_stem')['eid'].unique().to_dict()
right_map = right_map.groupby('right_stem')['eid'].unique().to_dict()

# For each vessel row, find eids matched via stem in left_map or right_map
def eids_for_stem(s):
    eids = set()
    if pd.isna(s):
        return eids
    if s in left_map:
        eids.update(left_map[s])
    if s in right_map:
        eids.update(right_map[s])
    return eids

vessel['matched_eids'] = vessel['stem'].apply(eids_for_stem)

# Build per-eid flags
from collections import defaultdict
eid_has_left = defaultdict(bool)
eid_has_right = defaultdict(bool)

for s,row in vessel.iterrows():
    stem = row['stem']
    if pd.isna(stem):
        continue
    # which eids map via left/right separately
    if stem in left_map:
        for e in left_map[stem]:
            eid_has_left[e] = True
    if stem in right_map:
        for e in right_map[stem]:
            eid_has_right[e] = True

all_eids = set(pat['eid'].unique())
only_left = [e for e in all_eids if eid_has_left.get(e, False) and not eid_has_right.get(e, False)]
only_right = [e for e in all_eids if eid_has_right.get(e, False) and not eid_has_left.get(e, False)]
both = [e for e in all_eids if eid_has_left.get(e, False) and eid_has_right.get(e, False)]
none = [e for e in all_eids if not eid_has_left.get(e, False) and not eid_has_right.get(e, False)]

# Print summary
print('Vessel-row match counts:')
for k in ['left','right','both','none']:
    print(f'  {k}: {counts.get(k,0)}')

print('\nParticipant-level summary:')
print(f'  total participants: {len(all_eids)}')
print(f'  only_left: {len(only_left)}')
print(f'  only_right: {len(only_right)}')
print(f'  both_left_and_right: {len(both)}')
print(f'  none_matched: {len(none)}')

# Save CSV of only_right participants
out = pd.DataFrame({'eid': only_right})
out.to_csv(r'M:/NEW-PROJECT/AUTOMORPH/participants_only_right.csv', index=False)
print('\nSaved M:/NEW-PROJECT/AUTOMORPH/participants_only_right.csv')
