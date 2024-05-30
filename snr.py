from os import chdir
from os.path import join, isfile
import numpy as np
import mne
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st

def snr_flip_polarity(epo, picks, tw):

    # select half of the trials (every other trial)
            epo = epo.get_data(picks=picks, 
                        item = range(0,len(epo), 1), 
                        tmin=tw[0], tmax=tw[-1])
            epo = np.mean(epo, axis = 1) # average over channel

            if not (len(epo) % 2) == 0: # delete last trial if number of trials is odd
                  epo=epo[:-1]                   
            
            signal = np.mean(epo, axis=0) # average trials
            signal = signal**2 # square them
            signal = np.mean(signal, axis=0) # average
            rms_signal = np.sqrt(signal)
            
            epon = epo[0:len(epo)-1:2]*-1 # reverse polarity (flip) of signal for one half of the trials
            epop = epo[1:len(epo):2]
        
            noise = np.concatenate((epop, epon))
            noise = np.mean(noise, axis = 0) # average trials
            noise = noise**2 # square them
            noise = np.mean(noise, axis = 0) # average
            rms_noise = np.sqrt(noise)
            
            
            # divide signal RMS by noise RMS
            snr = rms_signal/rms_noise

            return snr
    

outdir = ("...")
chdir(outdir)

participants = [4,5,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39] # only participants with >70% trials retained


MMN = {"name": "MMN",
       "picks_wet": ["FCz"], 
       "picks_dry": ["3Z"],
       "tw": [0.1, 0.15]}

erps=[MMN]

table = np.array([['ID', 'erp', 'system', 'snr']])

for sub in participants:
    if isfile(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif")) and isfile(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif")):
        
        # load epochs from normal EEG
        epochs = mne.read_epochs(join(outdir, "Nass", "final", f"{sub}_NA_TOENE_clean_epo.fif"))       
        
        # select trials, only deviants?
        epo = epochs['deviant1', 'deviant2']

        for erp in erps:        
            # select half of the trials (every other trial)
            snr = snr_flip_polarity(epo, erp["picks_wet"], erp["tw"])

            table = np.append(table,[[sub, erp["name"], "Nass", snr]], axis = 0)
        
        # load epochs from dry EEG
        epochs = mne.read_epochs(join(outdir, "Trocken Artefact Corrected", "final", f"{sub}_TR_TOENE_clean_epo.fif"))       
        
        # select trials, only deviants
        epo = epochs['deviant1', 'deviant2']

        for erp in erps:
              snr = snr_flip_polarity(epo, erp["picks_dry"], erp["tw"])

              table = np.append(table,[[sub, erp["name"], "Trocken", snr]], axis = 0)

snr_all = pd.DataFrame(table[1:,], columns=[list(table[0,])])

snr_all.to_csv(".../snr.csv")
