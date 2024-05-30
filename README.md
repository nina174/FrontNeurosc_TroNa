# FrontNeurosc_TroNa
This is all the code regarding the preprocessing, ERP, time-frequency and statistical analysis for the TroNa-project comparing wet- and dry EEG recordings as presented in the manuscript submitted to Frontiers in Neuroscience. 

## Preprocessing of EEG data
0. Create montage for dry EEG with *make_montage_dry_eeg.py*
1. Run *open_raw.py*

   Loads the data, sets references and montages, opens a window to mark bad channels or loads .txt-file that contains names of bad channels (if already exists).
2. Run *epoching.py*

   Loads *…raw.fif* from step 1, filters the data, creates epochs, resampling. 
3. Run *ica.py*

   Loads *…epo.fif* from step 2, re-references the EOGs, ICA, components correlating with EOGs are rejected, interpolation of bad channels.
4. Run *artifact_rejection.py*

   Loads *…ica_epo.fif* from step 3, rejects trials containing artifacts according to criteria set in line 43/44 and 46, equalize event counts of relevant conditions.
5. Run *summarize_preproc.py*

   Returns descriptives and statistics of preprocessing for wet vs. dry EEG.

## ERP analysis
### Time-domain
1.	Run *extract_ERPs_singlechans.py*

  	Loads data from preprocessing after step 4, applies baseline correction, accumulates for all participants (averaged over time points and electrodes), extracts peak latency and amplitude for each participant
2. Run *snr.py*

   Calculates the SNR using the method described by Viola et al. (2011) (DOI: 10.1111/j.1469-8986.2011.01224.x) based on data from preprocessing after step 4.
3. Run *stats_MMN.R*

   Calculates descriptives for MMN mean and peak amplitude, peak latency, SNR from step 1 and 2, ANOVA with system x tone interaction for MMN measures and follow-up t-tests, t-test for SNR between dry and wet EEG, raincloud plots for SNR and MMN (mean amplitude) and Bland-Altman plots for MMN characteristics.
4. Run *plot_ERPs.py*

   Plots MMN curves.
5. Run *plot_topos.py*

   Plots MMN topography. 

### Frequency-domain
1. Run *TFA_ft.m*

   Loads data from preprocessing after step 4, time-frequency analyses for standard and deviant tones separately
2. Run *GAs_ft.m*

   Loads time-frequency data from step 1, averages over trials for each participant and accumulates for all participants
3. Run *stats_TFA_ft.m*

   Baseline-corrects grand averages from step 2, extracts data for statistical analysis in R, plots power spectra
4.	Run *stats_theta.R*

  	ANOVA with system x tone interaction for extracted MMN theta power from step 4 and follow-up t-tests, raincloud and Bland-Altman plot for MMN theta power.

## Resting-state analysis
1. preprocessed data after step 3 is analyzed in Brainwave.
2. 




Python version 3.11.4, MNE version 1.4.2., Matlab R2019a, Fieldtrip version fieldtrip-20211016, R version 4.3.3 (2024-02-29), RStudio 2023.12.1. 

 



