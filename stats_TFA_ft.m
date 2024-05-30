cd("...") # path to dry or wet EEG output

%% load GAs and BL-correct 
load('GAPOW_std.mat');

cfg.baseline     = [-0.6 -0.3];
% cfg.baseline     = [-0.15 -0.05];
cfg.baselinetype = 'db';
cfg.parameter    = 'powspctrm';
grandavg_std         = ft_freqbaseline(cfg, grandavg);
% grandavg_std = grandavg;

load('GAPOW_dev.mat');

cfg.baseline     = [-0.6 -0.3];
% cfg.baseline     = [-0.15 -0.05];
cfg.baselinetype = 'db';
cfg.parameter    = 'powspctrm';
grandavg_dev         = ft_freqbaseline(cfg, grandavg);
% grandavg_dev = grandavg;

%% extract data for R

cfg = [];
cfg.channel = '3Z';
cfg.latency = [0.1 0.3];
cfg.avgovertime = 'yes';
cfg.frequency = [4 8];
cfg.avgoverfreq = 'yes';
std = ft_selectdata(cfg, grandavg_std);
dev = ft_selectdata(cfg, grandavg_dev);

participants = [4;5;6;7;8;9;12;13;14;15;17;18;19;20;21;22;23;24;25;29;31;33;37;39];
tone = [repmat({"std"}, length(participants),1); repmat({"dev"}, length(participants),1)]; 
amp = [std.powspctrm; dev.powspctrm];
participants = vertcat(participants, participants);

dat = table(participants, tone, amp);
writetable(dat,'.../theta.csv') 

%% plot

% calculate MMN

cfg = [];
cfg.parameter = 'powspctrm'; 
cfg.operation = 'subtract';
mmn = ft_math(cfg, grandavg_dev, grandavg_std);

% topography
figure
cfg = [];
cfg.parameter = 'powspctrm';
cfg.xlim = [0.1 0.3];
cfg.ylim = [3 8];
% cfg.zlim = [-0.4 0.4];
cfg.layout = lay;
cfg.colorbar = 'yes';
ft_topoplotTFR(cfg, mmn)

set(gcf, 'color','white')
a = colorbar;

% power spectrum
cfg = [];
% cfg.baseline     = [-0.5 -0.3];
% cfg.baselinetype = 'absolute';
cfg.ylim = [4 8];
cfg.xlim = [0 0.5];
cfg.zlim = [0 1.2];
cfg.channel = 'FCz';
ft_singleplotTFR(cfg, mmn)

set(gcf, 'color','white')
xlabel('time in seconds')
ylabel('frequency in Hz')
a = colorbar;
ylabel(a, 'dev - std', 'FontSize', 12);
