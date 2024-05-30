# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:15:42 2023

@author: ehrhardtn
"""

from os import chdir, listdir
from os.path import join, isfile
from glob import glob
import mne

## Import data ##############################################################

root_dir = ("...")
out_dir = ("...")

system = ["Nass", "Trocken Artefact Corrected"]
condition = ["TOENE", "REEG1"]

overwrite = False

for sys in system:
    
    sys_dir = join(root_dir, f"{sys}")
    chdir(sys_dir)
    
    for cond in condition:
             
        filenames = listdir(sys_dir)
        
        for filename in filenames:

            file = filename.partition("202")
            sub = filename.partition("_")
            sub = sub[0]    
                        
            if filename[-5:] != ".vhdr" or f"{cond}" not in filename or sub in ["1", "11"]:
                continue
            
            if not overwrite and isfile(join(out_dir, f"{sys}", "final", f"{file[0]}epo.fif")):
                continue
            eeg_data = mne.io.read_raw_fif(join(out_dir, f"{sys}", "final", f"{file[0]}raw.fif"), preload = True)
            
            ## Filter the data            
            eeg_data.filter(l_freq=0.1, h_freq = 25, picks=['eog', 'eeg'])
            
            ## Trial definition
            if cond=="TOENE":
                events, event_id = mne.events_from_annotations(eeg_data, regexp='Stimulus')
            
                event_dict = {'standard1': 1, 'standard2': 2,
                          'deviant1': 3, 'deviant2': 4}
            
                epochs = mne.Epochs(eeg_data, events, event_id=event_dict, 
                                    tmin=-1.2, tmax=1.2, 
                                    preload=True, baseline=None) #automatic baseline correction from tmin to 0, but can be customized with the baseline parameter)
                
            else:
                rs_data = eeg_data.crop(tmin=eeg_data.annotations.onset[2], tmax=eeg_data.annotations.onset[3], include_tmax=True)
                epochs = mne.make_fixed_length_epochs(rs_data, duration=8, preload=True)
            
            epochs.resample(512, npad='auto', window='boxcar')
                
            ch_file = glob(join(out_dir, f"{sys}", "final", f"{sub}*badch.txt"))[0]
            with open(ch_file, 'r') as f:
                bad_ch = [line.rstrip('\n') for line in f]
            
            epochs.info['bads'] = bad_ch
            
            ## Save preprocessed data
            
            epochs.save(join(out_dir, f"{sys}", "final", f"{file[0]}epo.fif"), overwrite=overwrite)
                
