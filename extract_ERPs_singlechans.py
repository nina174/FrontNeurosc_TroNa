from os.path import join, isfile
import numpy as np
import mne
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st

outdir = ("...")

## first prepare data
participants = [4,5,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39] # only participants with >70% trials retained
MMN = {"name": "MMN",
       "picks_wet": ["FCz"], 
       "picks_dry": ["3Z"],
       "tw": [0.1, 0.15]}

erps=[MMN]
average_times = True
equal_events = True

table = np.array([['ID', 'erp', 'system', 'latency', 'amplitude']])

for erp in erps:

    std_all_na = list()
    dev_all_na = list()
    std_all_tr = list()
    dev_all_tr = list()

    for sub in participants:
        if isfile(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif")) and isfile(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif")):
            
            # load epochs from dry EEG            
            epochs = mne.read_epochs(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif"))       
            epochs.crop(tmin=-0.1, tmax=erp["tw"][-1])
            trls = len(epochs['standard2'])

            # average trials with standard tone and apply baseline correction
            stand = epochs['standard2'].average(picks=erp["picks_dry"]).apply_baseline(baseline=(-0.1,0))
            
            # average trials with deviant tones and apply baseline correction
            dev = epochs['deviant1', 'deviant2'].average(picks=erp["picks_dry"]).apply_baseline(baseline=(-0.1,0))
            
            # get subject peak values
            erp_sub = mne.EvokedArray(dev.data-stand.data, stand.info) 
            _,lat, amp = erp_sub.get_peak(tmin=erp["tw"][0], tmax=erp["tw"][-1], return_amplitude=True)
            table = np.append(table,[[sub, erp["name"], "Trocken", lat, amp]], axis = 0)

            stand.crop(tmin=erp["tw"][0], tmax=erp["tw"][-1])
            stand = np.mean((stand.data), axis=0) # average over channels
            if average_times:
                stand = np.mean(stand, axis=0) # average time points
            
            # stack averages of standard tones from one channel in one array for all participants
            std_all_tr.append(stand)
            
            dev.crop(tmin=erp["tw"][0], tmax=erp["tw"][-1])
            dev = np.mean((dev.data), axis=0) # average over channels
            if average_times:
                dev = np.mean(dev, axis=0) # average over time points
            
            # stack averages of deviant tones from one channel in one array for all participants
            dev_all_tr.append(dev)

            # load epochs from normal EEG
            epochs = mne.read_epochs(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif"))       
            epochs.crop(tmin=-0.1, tmax=erp["tw"][-1])

            # average trials with standard tone and apply baseline correction
            stand = epochs['standard2'][0:trls] # select same no. of trials as dry EEG
            stand = stand.average(picks=erp["picks_wet"]).apply_baseline(baseline=(-0.1,0))
            
            # average trials with deviant tones and apply baseline correction
            dev = epochs['deviant1', 'deviant2'][0:trls]
            dev = dev.average(picks=erp["picks_wet"]).apply_baseline(baseline=(-0.1,0))
            
            # get subject peak values
            erp_sub = mne.EvokedArray(dev.data-stand.data, stand.info) 
            _,lat, amp = erp_sub.get_peak(tmin=erp["tw"][0], tmax=erp["tw"][-1], return_amplitude=True)
            table = np.append(table,[[sub, erp["name"], "Nass", lat, amp]], axis = 0)

            stand.crop(tmin=erp["tw"][0], tmax=erp["tw"][-1])
            stand = np.mean((stand.data), axis=0) # average over channels
            if average_times:
                stand = np.mean(stand, axis=0) #average over time points
            
            # stack averages of standard tones in one array for all participants
            std_all_na.append(stand) 
            
            dev.crop(tmin=erp["tw"][0], tmax=erp["tw"][-1])
            dev = np.mean((dev.data), axis=0) # average over channels
            if average_times:
                dev = np.mean(dev, axis=0) # average over timepoints
            
            # stack averages of deviant tones from one channel in one array for all participants
            dev_all_na.append(dev) 
                
            
    erp_na = list(np.array(dev_all_na) - np.array(std_all_na))
    erp_tr = list(np.array(dev_all_tr) - np.array(std_all_tr))

    dct = {"ID": participants,
        "dev_na": dev_all_na,
        "std_na": std_all_na,
        "diff_na": erp_na,
        "dev_tr": dev_all_tr,
        "std_tr": std_all_tr,
        "diff_tr": erp_tr
        }
    df = pd.DataFrame(dct)

    df.to_csv(f".../mean_amp_{erp['name']}.csv", index=False)

peaks = pd.DataFrame(table[1:,], columns=[list(table[0,])])
peaks.to_csv(".../peaks.csv", index=False)
