# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 14:25:20 2023

@author: ehrhardtn
"""

from os import chdir, listdir
from os.path import join, isfile
import numpy as np
import mne

## Import data ##############################################################

out_dir = ("...")

system = ["Nass", "Trocken Artefact Corrected"]
condition = ["TOENE", "REEG1"]

overwrite = True
equal_events = True

for sys in system:
     
    chdir(join(out_dir, f"{sys}", "final"))
    
    filenames = listdir()
    
    for cond in condition:
        
        table = np.array([['ID', 'no. rejected channel', '% rejected trials']])
    
        for filename in filenames:

            file = filename.partition("ica")  

            if "ica_epo.fif" not in filename:
                continue

            if not overwrite and isfile(f"{file[0]}clean_epo.fif"):
                continue
        
            epochs = mne.read_epochs(filename)
            epochs.reject_tmin=-0.1
            epochs.reject_tmax=0.5
            
            reject_criteria = dict(eeg=150e-6)       # 
            clean_epochs = epochs.copy()
            clean_epochs.drop_bad(reject=reject_criteria)
            #clean_epochs.plot_drop_log()
            # print(clean_epochs.drop_log)

            rej_trls = [n for n, dl in enumerate(clean_epochs.drop_log) if len(dl)] # find indices of rejected trials
            if rej_trls:
                rej_trls = np.array(rej_trls)
                rej_trls = np.c_[rej_trls, epochs.events[rej_trls,2]] # add event marker of rejected trials
            
            #mne.Epochs.plot(clean_epochs, picks='all', n_channels=len(epochs.ch_names), scalings=25e-6, events=events)
            
            if equal_events:
                clean_epochs.equalize_event_counts(event_ids=["standard2", ["deviant1", "deviant2"]])
            
            clean_epochs = clean_epochs["standard2", "deviant1", "deviant2"]

            sub = filename.partition("_")
            sub = sub[0]
                                  
            table = np.append(table,[[sub, len(epochs.info['bads']), 100*(len(rej_trls)/len(epochs.events))]], axis = 0)
            
            clean_epochs.save(f"{file[0]}clean_epo.fif", overwrite=overwrite)
            np.savetxt(f"{file[0]}rejtrls.txt", rej_trls, fmt='%d')
            
        np.save(f"{cond}_preprocessing.npy", table)
        
