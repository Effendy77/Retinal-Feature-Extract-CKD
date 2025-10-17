"""
Synthetic demo for AUTOMORPH preprocessing
- Writes tiny synthetic `vessel_features_merged.csv` and `retina_ckd_survival_ready_PAIRED.csv` into the AUTMORPH folder
- Runs the main script `Creating new image and participant level QC.py` using the same Python interpreter
- Prints small samples of the outputs for quick verification
"""
import os
import pandas as pd
import subprocess
import sys

ROOT = r"M:/NEW-PROJECT/AUTOMORPH"
os.makedirs(ROOT, exist_ok=True)

# Create synthetic participant table (6 participants with mixed left/right availability)
pat = pd.DataFrame({
    'eid': [1001,1002,1003,1004,1005,1006],
    'left_image_filename': ['1001_21015_0_0.jpg','1002_21015_0_0.jpg', pd.NA, '1004_21015_0_0.jpg','1005_21015_0_0.jpg', pd.NA],
    'right_image_filename': [pd.NA, '1002_21016_0_0.jpg','1003_21016_0_0.jpg','1004_21016_0_0.jpg', pd.NA, '1006_21016_0_0.jpg']
})
pat_fp = os.path.join(ROOT, 'retina_ckd_survival_ready_PAIRED.csv')
pat.to_csv(pat_fp, index=False)

# Create synthetic vessel features for some image files
vessel_rows = []
# image for 1001 left
vessel_rows.append({'original_filename':'1001_21015_0_0.jpg', 'height':100, 'width':120, 'area_px':1200, 'vessel_density':0.32})
# 1002 left and right
vessel_rows.append({'original_filename':'1002_21015_0_0.jpg', 'height':98, 'width':118, 'area_px':1156, 'vessel_density':0.30})
vessel_rows.append({'original_filename':'1002_21016_0_0.jpg', 'height':101, 'width':119, 'area_px':1201, 'vessel_density':0.33})
# 1003 only right
vessel_rows.append({'original_filename':'1003_21016_0_0.jpg', 'height':95, 'width':110, 'area_px':1045, 'vessel_density':0.28})
# 1004 both
vessel_rows.append({'original_filename':'1004_21015_0_0.jpg', 'height':102, 'width':125, 'area_px':1275, 'vessel_density':0.35})
vessel_rows.append({'original_filename':'1004_21016_0_0.jpg', 'height':103, 'width':126, 'area_px':1298, 'vessel_density':0.36})
# 1005 left only
vessel_rows.append({'original_filename':'1005_21015_0_0.jpg', 'height':99, 'width':115, 'area_px':1138, 'vessel_density':0.31})
# 1006 right only
vessel_rows.append({'original_filename':'1006_21016_0_0.jpg', 'height':100, 'width':120, 'area_px':1200, 'vessel_density':0.29})

vessel = pd.DataFrame(vessel_rows)
vessel_fp = os.path.join(ROOT, 'vessel_features_merged.csv')
vessel.to_csv(vessel_fp, index=False)

print('Wrote synthetic files:')
print('  ', pat_fp)
print('  ', vessel_fp)

# Run the main preprocessing script using the current Python interpreter (or adjust path)
main_script = os.path.join(ROOT, 'Creating new image and participant level QC.py')
print('\nRunning preprocessing script...')
cmd = [sys.executable, main_script]
proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
print('Return code:', proc.returncode)
print('Stdout:\n', proc.stdout)
print('Stderr:\n', proc.stderr)

# Show generated outputs (aggregated file)
agg_fp = os.path.join(ROOT, 'master_participant_level_single_image_aggregated.csv')
if os.path.exists(agg_fp):
    df = pd.read_csv(agg_fp)
    print('\nAggregated file sample:')
    print(df.head(10).to_string(index=False))
else:
    print('\nAggregated file not found:', agg_fp)

# Eye used file
eye_fp = os.path.join(ROOT, 'master_participant_eye_used.csv')
if os.path.exists(eye_fp):
    print('\nEye used:')
    print(pd.read_csv(eye_fp).to_string(index=False))
else:
    print('\nEye-used file not found:', eye_fp)
