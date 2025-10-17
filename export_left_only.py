import pandas as pd
import os

OUTPUT_DIR = r"M:/NEW-PROJECT/AUTOMORPH"

full_fp = os.path.join(OUTPUT_DIR, 'master_participant_level_single_image.csv')
agg_fp = os.path.join(OUTPUT_DIR, 'master_participant_level_single_image_aggregated.csv')
eyes_fp = os.path.join(OUTPUT_DIR, 'master_participant_eye_used.csv')

out_full = os.path.join(OUTPUT_DIR, 'master_participant_level_left_only.csv')
out_agg = os.path.join(OUTPUT_DIR, 'master_participant_level_left_only_aggregated.csv')

# Load
full = pd.read_csv(full_fp, low_memory=False)
agg = pd.read_csv(agg_fp, low_memory=False)
eyes = pd.read_csv(eyes_fp, low_memory=False)

# Merge eye_used into agg if needed
agg = agg.merge(eyes, on='eid', how='left')

# Filter where eye_used == 'left'
full_left = full[full['used_left'] == True].copy()
agg_left = agg[agg['eye_used'] == 'left'].copy()

# Save
full_left.to_csv(out_full, index=False)
# Drop eye_used column from aggregated output for cleanliness
if 'eye_used' in agg_left.columns:
    agg_left = agg_left.drop(columns=['eye_used'])
agg_left.to_csv(out_agg, index=False)

print('Saved left-only:')
print('  ', out_full)
print('  ', out_agg)
print('Counts: full_left=', len(full_left), ' agg_left=', len(agg_left))
