from os.path import join, isfile
import numpy as np
import mne
import matplotlib.pyplot as plt
from math import sqrt

outdir = ("...")

## first prepare data

std_all_na = np.array([])
dev_all_na = np.array([])
std_all_tr = np.array([])
dev_all_tr = np.array([])

participants = [4,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39] # only participants with >70% trials and SNR above 1 retained, 

chan_wet = ["FCz"]
chan_dry = ["3Z"]


for sub in participants:
    if isfile(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif")) and isfile(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif")):
        
        # load epochs from normal EEG
        epochs = mne.read_epochs(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif"))       
        epochs.crop(tmin=-0.1, tmax=0.5)
        # average trials with standard tone and apply baseline correction
        stand = epochs['standard2'].average(picks=chan_wet).apply_baseline(baseline=(-0.1,0))
        
        stand = stand.data
        #stand = np.expand_dims(stand, axis = 0) # add second dimension to stack participants
        
        # stack averages of standard tones in one array for all participants
        if len(std_all_na) == 0:
            std_all_na = stand
        else:
            std_all_na = np.row_stack((std_all_na, stand))
        
        # average trials with deviant tones and apply baseline correction
        dev = epochs['deviant1', 'deviant2'].average(picks=chan_wet).apply_baseline(baseline=(-0.1,0))
        
        dev = dev.data
        #dev = np.expand_dims(dev.data, axis = 0) # add second dimension to stack participants
        
        # stack averages of deviant tones from one channel in one array for all participants
        if len(dev_all_na) == 0:
            dev_all_na = dev
        else:
            dev_all_na = np.row_stack((dev_all_na, dev))
            
        # load epochs from dry EEG            
        epochs = mne.read_epochs(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif"))       
        epochs.crop(tmin=-0.1, tmax=0.5)
        # average trials with standard tone and apply baseline correction
        stand = epochs['standard2'].average(picks=chan_dry).apply_baseline(baseline=(-0.1,0))
        
        stand = stand.data
        #stand = np.expand_dims(stand.data, axis = 0) # add second dimension to stack participants
        
        # stack averages of standard tones from one channel in one array for all participants
        if len(std_all_tr) == 0:
            std_all_tr = stand
        else:
            std_all_tr = np.row_stack((std_all_tr, stand))
        
        # average trials with deviant tones and apply baseline correction
        dev = epochs['deviant1', 'deviant2'].average(picks=chan_dry).apply_baseline(baseline=(-0.1,0))
        
        dev = dev.data
        #dev = np.expand_dims(dev.data, axis = 0) # add second dimension to stack participants
        
        # stack averages of deviant tones from one channel in one array for all participants
        if len(dev_all_tr) == 0:
            dev_all_tr = dev
        else:
            dev_all_tr = np.row_stack((dev_all_tr, dev))

    # plot ERPs with CI

    ci_na = 1.96 * np.std(dev_all_na.mean(axis=0) - std_all_na.mean(axis=0))/sqrt(len(participants))
    ci_tr = 1.96 * np.std(dev_all_tr.mean(axis=0) - std_all_tr.mean(axis=0))/sqrt(len(participants))

    times = epochs.times
    fig, ax = plt.subplots()
    # ax.set_title(f"Contrast (Deviant tones - Standard tones) {chan_wet} (wet), {chan_dry} (dry)")

    ax.plot(times, dev_all_na.mean(axis=0) - std_all_na.mean(axis=0),
            label="Wet", color = "#329562b4", alpha = .71)
    ax.fill_between(times, ((dev_all_na.mean(axis=0) - std_all_na.mean(axis=0))-ci_na),
                    ((dev_all_na.mean(axis=0) - std_all_na.mean(axis=0))+ci_na), 
                    color = "#2d9357ff", alpha = .23)  

    ax.plot(times, dev_all_tr.mean(axis=0) - std_all_tr.mean(axis=0),
            label="Dry", color = "#ff801040", alpha = .71)
    ax.fill_between(times, ((dev_all_tr.mean(axis=0) - std_all_tr.mean(axis=0))-ci_tr),
                    ((dev_all_tr.mean(axis=0) - std_all_tr.mean(axis=0))+ci_tr),
                    color = "#ff7f0eff", alpha = .25)  
    ax.axvspan(0.1, 0.15, color=(0.76, 0.76, 0.76),
                    alpha=0.25)
    ax.set_ylabel("Amplitude")
    ax.legend()
    plt.ylim(ymin = -0.000005, ymax = 0.000005)
    plt.gca().invert_yaxis()
    mm = 1/25.4  # mm in inches
    plt.gcf().set_size_inches(105.04*mm, 101.974*mm)
    # plt.draw()
    plt.savefig("ERP_plot_MMN.svg", format="svg", dpi=300)
