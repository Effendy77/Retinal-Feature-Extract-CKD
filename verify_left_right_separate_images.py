import pandas as pd

# Paths (same as used by your script)
participant_csv = "M:/NEW-PROJECT/AUTOMORPH/master_participant_level_left_right.csv"
pat_csv = "M:/NEW-PROJECT/AUTOMORPH/retina_ckd_survival_ready_PAIRED.csv"

# Load participant-level output
p = pd.read_csv(participant_csv, low_memory=False)

# Try to use left/right stem columns from participant; if missing, load original pat to get stems
if 'left_fname_stem' not in p.columns or 'right_fname_stem' not in p.columns:
    pat = pd.read_csv(pat_csv, low_memory=False)
    pat['left_fname_norm'] = pat['left_image_filename'].astype(str).str.strip().map(lambda x: x.split('/')[-1].lower())
    pat['left_fname_stem'] = pat['left_fname_norm'].str.replace(r'\.[a-z0-9]+$', '', regex=True)
    pat['right_fname_norm'] = pat['right_image_filename'].astype(str).str.strip().map(lambda x: x.split('/')[-1].lower())
    pat['right_fname_stem'] = pat['right_fname_norm'].str.replace(r'\.[a-z0-9]+$', '', regex=True)
    # Join stems into participant table
    p = p.merge(pat[['eid','left_fname_stem','right_fname_stem']], on='eid', how='left')

# Identify participants with two-eye features
if 'num_images_with_features' in p.columns:
    both = p[p['num_images_with_features'] == 2].copy()
else:
    both = p[p[['has_left_features','has_right_features']].all(axis=1)].copy()

n_both = len(both)
print(f"Participants with both-eye features (from file): {n_both}")

# Compare stems
both['stems_equal'] = (both['left_fname_stem'] == both['right_fname_stem'])

n_equal = both['stems_equal'].sum()
n_diff = n_both - n_equal
print(f"Left/right stems equal: {n_equal}")
print(f"Left/right stems different: {n_diff}")

# Show a sample of differing cases
print('\nSample of participants where stems differ (first 20):')
print(both.loc[~both['stems_equal'], ['eid','left_fname_stem','right_fname_stem']].head(20).to_string(index=False))

# If left/right stems are different, parameters were taken from different image files (by filename)
print('\nInterpretation: if stems differ, the left and right features come from different image files; merging/averaging will combine measurements from different images.')

# Save a CSV listing differing cases for your review
both.loc[~both['stems_equal'], ['eid','left_fname_stem','right_fname_stem']].to_csv('participants_both_stems_differ.csv', index=False)
print('\nSaved participants_both_stems_differ.csv (list of eids with differing stems).')
