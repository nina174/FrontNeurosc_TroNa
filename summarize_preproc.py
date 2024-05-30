# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 15:02:37 2023

@author: ehrhardtn
"""

from os import chdir, listdir
from os.path import join
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel

## Import data ##############################################################

out_dir = ("...")
rs_dir  = ("...")
system  = ["Nass", "Trocken Artefact Corrected"]
condition = ["TOENE", "REEG1"]

# participants = [4,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39] # only participants with >70% trials retained and SNR above 1
participants = [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,29,2,31,33,35,37,39,3,4,5,6,7,8,9] # participants included in RS

col_names = ('ID', 'no. rejected channel', 'system')
rej_chan = dict.fromkeys(col_names) 
rej_chan["ID"] = []
rej_chan["no. rejected channel"] = []
rej_chan["system"] =[]

col_names = ("ID", "% rejected trials")
rej_trls = pd.DataFrame(columns = col_names)

col_names = ("ID", "no. rejected components")
rej_comps = pd.DataFrame(columns = col_names)

for sys in system:
        
    chdir(join(out_dir, f"{sys}", "final"))
    
    filenames = listdir()
    
    for filename in filenames:
            
        if "_badch.txt" not in filename:
            continue
        
        sub = filename.partition("_")
        sub = int(sub[0])
        
        if sub not in participants:
            continue
        
        with open(filename, 'r') as fp:
            x = len(fp.readlines())  
                                                        
            rej_chan['ID'].append(sub)
            rej_chan['no. rejected channel'].append(x)
            rej_chan['system'].append(sys)
    
    data = np.load("TOENE_preprocessing.npy")
        
    d = pd.DataFrame(columns = data[0, :], 
                     data = data[1:,:]
                     )
    d = (d
            .drop(columns = "no. rejected channel") # deletes empty column
            .astype({
                # datentypen umstellen
                "ID": "int32", 
                "% rejected trials": "float64"
            })
            .assign(
                system = sys
            )
        )

    if len(rej_trls) == 0: # if the dataframe is empty...
        rej_trls = d # ...replace the dataframe
    else:
        rej_trls = pd.concat([rej_trls, d]) # ...otherwise append it
        
    for cond in condition:
        if cond=="TOENE":
            data = np.load(f"no_rej_components_{cond}.npy")
        else:
            data = np.load(join(rs_dir, f"{sys}", "ERP_Analysis", f"no_rej_components_{cond}.npy"))
        
        d = pd.DataFrame(
                columns = data[0, :],
                data = data[1:,:],
            )
        d = (d
                .astype({
                    # get the right datatypes
                    "ID": "int32", 
                    "no. rejected components": "float64"
                })
                .assign(
                    system = sys,
                    condition = cond
                )
            )

        if len(rej_comps) == 0: # if the dataframe is empty...
            rej_comps = d # ...replace the dataframe
        else:
            rej_comps = pd.concat([rej_comps, d]) # ...otherwise append it

print(rej_comps)
print(rej_trls)

rej_chan = pd.DataFrame.from_dict(rej_chan)
(rej_chan
    .drop(columns="ID")
    .groupby(["system"])
    .agg(["mean", "std", "min", "max"])
    .round(2)
)
rej_chan = rej_chan[rej_chan.ID.isin(participants)]
ttest_rel(rej_chan["no. rejected channel"][rej_chan["system"]=="Nass"],
          rej_chan["no. rejected channel"][rej_chan["system"]=="Trocken Artefact Corrected"]
          )

(rej_comps
    [rej_comps.ID.isin(participants)] 
    .drop(columns="ID")
    .groupby(["system", "condition"])
    .agg(["mean", "std", "min", "max"])
    .round(2)
)

rej_comps = rej_comps[rej_comps.ID.isin(participants)]

# comparison for task data
ttest_rel(rej_comps["no. rejected components"][(rej_comps["system"]=="Nass") & (rej_comps["condition"]=="TOENE")],
          rej_comps["no. rejected components"][(rej_comps["system"]=="Trocken Artefact Corrected") & (rej_comps["condition"]=="TOENE")]
          )
# comparison for rs data
ttest_rel(rej_comps["no. rejected components"][(rej_comps["system"]=="Nass") & (rej_comps["condition"]=="REEG1")],
          rej_comps["no. rejected components"][(rej_comps["system"]=="Trocken Artefact Corrected") & (rej_comps["condition"]=="REEG1")]
          )


(rej_trls
    [rej_trls.ID.isin(participants)]
    .drop(columns="ID")
    .groupby(["system"])
    .agg(["mean", "std", "min", "max"])
    .round(2)
)

rej_trls = rej_trls[rej_trls.ID.isin(participants)]

ttest_rel(rej_trls["% rejected trials"][rej_trls["system"]=="Nass"],
          rej_trls["% rejected trials"][rej_trls["system"]=="Trocken Artefact Corrected"]
          )
