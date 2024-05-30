participants = [4,5,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39]; 
cd("...")

Grandav = struct();

for s = 1:length(participants)
    
    
    load(sprintf('%d_TR_stand_tfa_ft.mat', participants(s))); 
    std_TFRwave = TFRwave;
    
    if contains(pwd, "Nass")
        load(sprintf(".../%d_TR_stand_tfa_ft.mat", participants(s)))
        
        trls = size(TFRwave.powspctrm,1);
        clear TFRwave
        
    else 
        trls = size(std_TFRwave.powspctrm,1);
    end
    
    if contains(pwd, "Nass")
        load(sprintf(".../%d_TR_stand_tfa_ft.mat", participants(s)))
        
        trls = size(TFRwave.powspctrm,1);
        clear TFRwave
        
    else 
        trls = size(std_TFRwave.powspctrm,1);
    end

    % Average over trials
    cfg = [];
    cfg.trials = 1:trls;
    cfg.keeptrials = 'no';
    aTFRwave = ft_freqdescriptives(cfg, std_TFRwave);
    
%     % plot
%     cfg = [];
%     cfg.baseline     = [-0.6 -0.3];
%     cfg.baselinetype = 'absolute';
%     cfg.ylim = [3 8];
%     cfg.xlim = [0 0.5];
%     cfg.channel = 'load(sprintf('%d_TR_dev_tfa_ft.mat', participants(s)));Cz';
%     ft_singleplotTFR(cfg, TFRwave)

    Grandav(s).aTFRwave = aTFRwave;
   
end

% GA standard tones 

cfg = [];
cfg.keepindividual = 'yes';
cfg.foilim         = 'all';
cfg.toilim         = 'all'; % early: 0.1-2.9load(sprintf('%d_TR_dev_tfa_ft.mat', participants(s))); late: 3.1-5.9
cfg.channel        = 'all';                     
cfg.parameter      = 'powspctrm';% 'crsspctrm'

grandavg = ft_freqgrandaverage(cfg, Grandav.aTFRwave);

save('GAPOW_std', 'grandavg', '-v7.3');

for s = 1:length(participants)
      
    load(sprintf('%d_TR_dev_tfa_ft.mat', participants(s)));
    dev_TFRwave = TFRwave;
    % Average over trials and write in Grandav variable for all
    % participants
    
    if contains(pwd, "Nass")
        load(sprintf(".../%d_TR_stand_tfa_ft.mat", participants(s)))
        
        trls = size(TFRwave.powspctrm,1);
        clear TFRwave
        
    else 
        trls = size(dev_TFRwave.powspctrm,1);
    end
   
    cfg = [];
    cfg.trials = 1:trls;
    cfg.keeptrials = 'no';
    aTFRwave = ft_freqdescriptives(cfg, dev_TFRwave);

    Grandav(s).aTFRwave = aTFRwave;
   
end

% GA deviant tones 

cfg = [];
cfg.keepindividual = 'yes';
cfg.foilim         = 'all';
cfg.toilim         = 'all'; % early: 0.1-2.9 late: 3.1-5.9
cfg.channel        = 'all';                     
cfg.parameter      = 'powspctrm';% 'crsspctrm'

grandavg = ft_freqgrandaverage(cfg, Grandav.aTFRwave);

save('GAPOW_dev', 'grandavg', '-v7.3');

