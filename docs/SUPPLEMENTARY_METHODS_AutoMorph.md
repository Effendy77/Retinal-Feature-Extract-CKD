# Supplementary Methods: Retinal vessel representations and vascular feature extraction

## Overview and scope
This supplementary material describes downstream processing of retinal vessel segmentation outputs used in this study. Retinal vessel segmentation was performed using AutoMorph, a validated external pipeline, and is treated as an upstream dependency. Full reproducibility is provided for all downstream steps, including vessel mask harmonisation, vascular feature curation, participant-level aggregation, and quality control.

## Automated retinal vessel segmentation
Binary retinal vessel segmentation masks were generated using AutoMorph, a validated automated deep learning pipeline for retinal vascular morphology analysis applied to colour fundus photographs. Segmentation was executed using the original AutoMorph implementation without architectural modification. As AutoMorph constitutes a publicly available upstream method, its internal training and optimisation procedures are not reproduced here.

Segmentation outputs consisted of pixel-wise vessel probability maps, which were binarised to generate vessel masks (vessel pixels = 1; background = 0). These masks served as the basis for both pixel-level vessel representations and image-level vascular morphology feature extraction.

## Vessel mask preprocessing for deep learning
For deep learning experiments, vessel masks were spatially resized to match the resolution of the corresponding fundus image inputs used by the retinal backbone network. Masks were treated as single-channel binary images and were used either as standalone vessel representations or fused with fundus image embeddings in multimodal and ablation experiments. No additional smoothing, thinning, or manual correction was applied.

## Retinal vascular morphology feature extraction
A prespecified set of twelve quantitative retinal vascular morphology parameters was derived from AutoMorph outputs. Feature extraction was performed at the image level, generating one feature vector per eye-specific fundus photograph. Only numeric vascular parameters were retained for modelling.

## Participant-level aggregation and eye handling
Image-level feature tables were merged with study metadata using participant identifiers (`eid`) and eye-specific image identifiers. To ensure participant-level independence, a primary single-eye dataset was constructed using the left eye where available, with fallback to the right eye if the left eye was unavailable. Left-only and right-only datasets were additionally generated for sensitivity analyses. An explicit indicator of the eye used was retained.

## Quality control
Quality control included exclusion of images with missing or failed segmentation outputs, incomplete feature vectors, or invalid participant-image mappings. Summary quality control reports are generated automatically by the pipeline.

## Reproducibility and code availability
All downstream processing steps are implemented in this repository. The code enables full reproduction of vascular feature tables and vessel-derived inputs used in the analyses, assuming availability of AutoMorph segmentation outputs.
