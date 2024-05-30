participants = [4,5,6,7,8,9,12,13,14,15,17,18,19,20,21,22,23,24,25,29,31,33,37,39]; 
cd("...")

for s = 1:length(participants)
    
    subj=participants(s);
%     fiff_file = sprintf('%d_NA_TOENE_clean_epo.fif', subj);
    fiff_file = sprintf('%d_TR_TOENE_clean_epo.fif', subj)

    cfg         = [];
    cfg.dataset = fiff_file;
    data     = ft_preprocessing(cfg);

    [eventlist, mappings] = fiff_read_events(fiff_file); % an epoch file contains events
    data.trialinfo = eventlist(:,3); % note that the events have been recoded w.r.t. the original trigger values  

    cfg = [];
    cfg.channel    = 'all';
    cfg.trials     = find(data.trialinfo == 2);
    cfg.keeptrials = 'yes';
    cfg.method     = 'wavelet';                
    cfg.width      = linspace(3, 10, length(2:1:18));
    cfg.output     = 'pow';	
    cfg.gwidth     = 2;
    cfg.foi        = 2:1:18;	                
    cfg.toi        = -1.2:0.05:1.2;	
%         cfg.pad        = 'maxperlen';
%         cfg.padtype    = 'zero';
    TFRwave = ft_freqanalysis(cfg, data);
    
    save(sprintf('%d_TR_stand_tfa_ft.mat', subj), 'TFRwave');
    
    cfg.trials = find(data.trialinfo == 3 | data.trialinfo == 4);
    TFRwave = ft_freqanalysis(cfg, data);
    
    save(sprintf('%d_TR_dev_tfa_ft.mat', subj), 'TFRwave');
        
end

% figure
% cfg = [];
% % cfg.baseline     = [-0.5 -0.3];
% % cfg.baselinetype = 'absolute';
% cfg.ylim = [3 8];
% cfg.xlim = [0 0.5];
% cfg.channel = 'FCz';
% ft_singleplotTFR(cfg, dev)
