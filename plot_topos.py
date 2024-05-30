from os.path import join, isfile
import pandas as pd
import numpy as np
import mne
import matplotlib.pyplot as plt

outdir = ("...")

## first prepare data

std_all_na = list()
dev_all_na = list()
std_all_tr = list()
dev_all_tr = list()

participants = [4,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39] # only participants with >70% trials retained and SNR above 1

montage_dir = ("...")
elec_pos = join(montage_dir, "positionfile.csv")
elec_df = pd.read_csv(elec_pos,delimiter=";") # x- und y-Koordinaten vertauscht
elec_df["xpos"] = (elec_df)["xpos"]*(-1) # rechts und links sind vertauscht -> invert x
elec_df = elec_df[128:198]
elec_dict = {}
for idx, row in elec_df.iterrows():
    elec_dict[row["Label"]] = np.array([row["xpos"],
                                        row["ypos"],
                                        row["zpos"]])
    elec_dict[row["Label"]] *= 7e-4 #preprocessing was done with 1e-3 but this seems more accurate for plotting
    

digmon = mne.channels.make_dig_montage(ch_pos=elec_dict)

for sub in participants:
    if isfile(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif")) and isfile(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif")):
        
        # load epochs from normal EEG
        epochs = mne.read_epochs(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif"))       
        epochs.crop(tmin=-0.1, tmax=0.5)

        # average trials with standard tone and apply baseline correction
        stand = epochs['standard2'].average(picks="eeg").apply_baseline(baseline=(-0.1,0))
        
        std_all_na.append(stand)
        
        # average trials with deviant tones and apply baseline correction
        dev = epochs['deviant1', 'deviant2'].average(picks="eeg").apply_baseline(baseline=(-0.1,0))
        
        dev_all_na.append(dev)
        
        # load epochs from dry EEG            
        epochs = mne.read_epochs(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif"))       
        epochs.set_montage(digmon)
        epochs.crop(tmin=-0.1, tmax=0.5)
        # average trials with standard tone and apply baseline correction
        stand = epochs['standard2'].average(picks="eeg").apply_baseline(baseline=(-0.1,0))
        
        std_all_tr.append(stand)
        
        # average trials with deviant tones and apply baseline correction
        dev = epochs['deviant1', 'deviant2'].average(picks="eeg").apply_baseline(baseline=(-0.1,0))
        
        dev_all_tr.append(dev)

ga_std_na = mne.grand_average(std_all_na)
ga_std_tr = mne.grand_average(std_all_tr)
ga_dev_na = mne.grand_average(dev_all_na)
ga_dev_tr = mne.grand_average(dev_all_tr)
vlim=(-3,3)

dev_minus_std_na = mne.combine_evoked([ga_dev_na, ga_std_na], weights=[1, -1])
dev_minus_std_tr = mne.combine_evoked([ga_dev_tr, ga_std_tr], weights=[1, -1])
dev_minus_std_na.plot_topomap(times=0.125, average=0.05, 
                              sphere=(0.0, 0.02, 0.00, 0.095), 
                              vlim=vlim, show=False)
# plt.draw()
plt.savefig("topoplot_MMN_na.svg", format="svg")
dev_minus_std_tr.plot_topomap(times=0.125, average=0.05, 
                              sphere=(0.0, -0.02, 0.0, 0.095), 
                              vlim=vlim, show=False)
# plt.draw()
plt.savefig("topoplot_MMN_tr.svg", format="svg")
