AUTOMORPH Preprocessing for Retinal Feature Extraction
This repository contains the Python scripts used to process and generate the participant-level datasets from the AUTOMORPH pipeline for the Retinal Feature Extraction experiments.

## Upstream dependency: AutoMorph
Retinal vessel segmentation is performed using AutoMorph, a publicly available automated retinal vascular analysis pipeline. This repository assumes availability of AutoMorph segmentation outputs and does not re-implement, retrain, or modify the segmentation algorithm.

## Scope of this repository
This repository provides full reproducibility for all downstream processing steps following vessel segmentation, including vascular feature curation, participant-level aggregation, eye-selection logic, and quality control.

## What this repository does NOT do
This repository does not train or modify the AutoMorph segmentation model.

## Relationship to supplementary methods and figures

This repository provides the **code and pipelines for extracting handcrafted retinal vascular features** from automated vessel segmentations.

The **methodological justification, exploratory analyses, and feature selection rationale** (including correlation analysis, distributional assessment, and PCA diagnostics) are documented separately in the companion repository:

👉 **https://github.com/Effendy77/retina-ckd-supplementary**

That repository contains the submission-ready **Supplementary Methods S1** and **Supplementary Figures S1–S5** referenced in the associated manuscripts.

Feature extraction code in this repository is **outcome-agnostic** and was applied identically across downstream tasks, including eGFR regression and ESRD risk/survival modelling.


Overview
The scripts in this repository process raw, image-level vessel feature data (vessel_features_merged.csv) and map it to a participant cohort (retina_ckd_survival_ready_PAIRED.csv). The primary output is a set of participant-level CSV files suitable for model training, with various strategies for handling left- and right-eye data.

Prerequisites
Python 3.8+

Conda package manager

Required Python packages: pandas, numpy

⚙️ Setup and Installation
Clone the repository:

Bash

git clone https://github.com/Effendy77/Retinal-Feature-Extract-CKD.git
cd Retinal-Feature-Extract-CKD
Create the Conda environment: An environment.yml file is provided for easy setup.

Bash

conda env create -f environment.yml
conda activate automorph_env
(Note: If you don't have an environment.yml file, you can create one from your working environment by running conda env export > environment.yml)

Place the data: Create a data directory inside the repository and place the two required source files inside it:

Retinal-Feature-Extract-CKD/
├── data/
│   ├── vessel_features_merged.csv
│   └── retina_ckd_survival_ready_PAIRED.csv
├── scripts/
│   ├── creating_new_image_and_participant_level_qc.py
│   └── ... (other scripts)
└── README.md
🚀 Usage: Generating the Datasets
All generated files will be placed in an output directory.

1. Generate the Primary Datasets
This script creates the main participant-level files and a QC report.

Bash

python scripts/creating_new_image_and_participant_level_qc.py
This will generate the following files in the output/ directory:

master_image_level.csv

master_participant_level_single_image.csv

master_participant_level_single_image_aggregated.csv

master_participant_eye_used.csv

qc_report.txt

2. Generate Left-Only and Right-Only Datasets
To create datasets for specific eye experiments, run the corresponding export scripts:

Bash

# Export left-eye only data
python scripts/export_left_only.py

# Export right-eye only data
python scripts/export_right_only.py
📂 Generated File Descriptions
Primary Files (One-Row-Per-Participant)
master_participant_level_single_image_aggregated.csv: Recommended for most models. One row per participant. Features are taken from the left eye if available, otherwise the right eye is used.

master_participant_level_single_image.csv: Full participant table with all metadata, including separate _left and _right feature columns.

master_participant_eye_used.csv: A helper file listing which eye (left or right) was used for each participant in the aggregated dataset.

Image-Level and QC Files
master_image_level.csv: Contains one row per image, including mapping status.

qc_report.txt: A summary of participant and image counts from the generation process.

Methodology
Feature Selection: Only numeric columns from the source data were aggregated as features.

Aggregation Logic: For the primary combined dataset, the final feature value is taken from the left eye's measurement. If a left-eye measurement is not available, the right eye's measurement is used as a fallback. The master_participant_eye_used.csv file tracks the source for each participant.

🧪 Suggested Experiments
Baseline Model: Train using master_participant_level_left_only_aggregated.csv (8,246 participants) to avoid any potential data leakage between eyes.

Combined Model: Train using master_participant_level_single_image_aggregated.csv (16,458 participants) to maximize sample size. Consider including the eye_used column as a feature to control for potential systemic differences between eyes.

Two-Eye Model: Use the detailed master_participant_level_single_image.csv to build a model that can explicitly use features from both eyes when available.

⚠️ Important Caveat on Cross-Validation
To avoid data leakage, always split your data at the participant level, not the image level. Ensure that both images from a single participant do not end up in different folds (e.g., one in training and one in testing).

Publishing Data
The scripts and this README should be committed to the Git repository. The large input and output CSV files should not be committed.

Instead, they should be packaged (e.g., in a .zip archive) and uploaded as a Release Asset on GitHub.

.gitignore
Use a .gitignore file to prevent large data files from being tracked by Git.

# Data files
data/
output/
*.csv
*.zip

# Python / Conda
__pycache__/
*.ipynb_checkpoints
.conda

