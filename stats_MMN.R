###############################################################################
###################### Statistical analyses ###################################
######################## TRONA T?ne MMN #######################################
######################### Nina Ehrhardt #######################################
###############################################################################

setwd("...")
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)
library(psych)
library(rstatix)
library(ggrain)
library(blandr)

excl <- c(5)

snr <- read.csv("snr.csv")
snr <-
  snr %>% mutate_at(c("erp", "system"), as.factor) %>%
  filter(!ID %in% excl)
snr$X <- NULL

peaks <- read.csv("peaks.csv")
peaks <-
  peaks %>% mutate_at(c("erp", "system"), as.factor) %>%
  filter(!ID %in% excl)

amp_mmn <- read.csv("mean_amp_MMN.csv")
amp_mmn <- amp_mmn %>%
  gather(condition, mean_amp, dev_na:diff_tr, factor_key=TRUE) %>%
  filter(!ID %in% excl)
amp_mmn$erp <- as.factor(rep("MMN", nrow(amp_mmn)))

mean_amp <- amp_mmn %>%
  separate(condition, c("tone", "system")) %>%
  mutate_at(c("tone", "system"), as.factor)

dat <- merge(snr, peaks, by=c("ID", "erp", "system"), all=TRUE)

####### stats ####

## MMN

mmn <- subset(mean_amp, erp == "MMN" & tone != "diff") 
ggplot(mmn, aes(x=tone, y=mean_amp, fill=tone)) +
  geom_rain(alpha = .5) +
  theme_classic() +
  scale_fill_brewer(palette = 'Dark2') +
  guides(fill = 'none', color = 'none') +
  facet_wrap(~system) +
  scale_y_reverse()

# assumptions
mmn %>%
  group_by(system, tone) %>%
  identify_outliers(mean_amp)

mmn %>%
  group_by(system, tone) %>%
  shapiro_test(mean_amp)

ggqqplot(mmn, "mean_amp", ggtheme = theme_bw()) +
  facet_grid(tone ~ system, labeller = "label_both")

# anova
res.aov <- anova_test(
  data = mmn, dv = mean_amp, wid = ID,
  within = c(tone, system),
  effect.size = "pes" # partial eta squared
)
get_anova_table(res.aov)

# FU tests tones

pwc <- mmn %>%
  group_by(system) %>%
  pairwise_t_test(
    mean_amp ~ tone, paired = TRUE,
    p.adjust.method = "bonferroni", 
    alternative = "less" #?
  )
pwc

# effect size tones
ef <- mmn %>%
  group_by(system) %>%
  cohens_d(
  mean_amp ~ tone,
  comparisons = NULL,
  ref.group = NULL,
  paired = TRUE,
  mu = 0,
  hedges.correction = FALSE,
  ci = FALSE,
  conf.level = 0.95,
  ci.type = "perc",
  nboot = 1000
)
ef

# FU tests system
mmn <- subset(mean_amp, erp == "MMN" & tone == "diff") 

describeBy(mmn, group="system", mat = TRUE, digits=8)

pwc <- mmn %>%
  pairwise_t_test(
    mean_amp ~ system, paired = TRUE
  )
pwc

# effect size system
ef <- mmn %>%
  cohens_d(
    mean_amp ~ system,
    comparisons = NULL,
    ref.group = NULL,
    paired = TRUE,
    mu = 0,
    hedges.correction = FALSE,
    ci = FALSE,
    conf.level = 0.95,
    ci.type = "perc",
    nboot = 1000
  )
ef


## ERP characteristics
peaks %>%
  pairwise_t_test(
    latency ~ system, paired = TRUE,
    p.adjust.method = "none"
  ) 
ef <- peaks %>%
  cohens_d(
    latency ~ system,
    comparisons = NULL,
    ref.group = NULL,
    paired = TRUE,
    mu = 0,
    hedges.correction = FALSE,
    ci = FALSE,
    conf.level = 0.95,
    ci.type = "perc",
    nboot = 1000
  )
ef

peaks %>%
  pairwise_t_test(
    amplitude ~ system, paired = TRUE,
    p.adjust.method = "none"
  )

ef <- peaks %>%
  cohens_d(
    amplitude ~ system,
    comparisons = NULL,
    ref.group = NULL,
    paired = TRUE,
    mu = 0,
    hedges.correction = FALSE,
    ci = FALSE,
    conf.level = 0.95,
    ci.type = "perc",
    nboot = 1000
  )
ef

# mean, sd, min, max
describeBy(dat, list(dat$system, dat$erp), mat=TRUE, digits = 9)



## SNR
snr %>%
  pairwise_t_test(
    snr ~ system, paired = TRUE,
    p.adjust.method = "none"
  )

describeBy(snr, group = "system")


####### Raincloud plot #####
ggplot(snr, aes(x = system, y = snr, fill = system)) + 
  geom_rain(alpha = .5) +
  theme_classic() +
  scale_fill_brewer(palette = 'Dark2') +
  guides(fill = 'none', color = 'none')


####### Bland Altman ######
diff_mean_amp <- subset(mean_amp, erp == "MMN" & tone == "diff") 
diff_wide <- pivot_wider(diff_mean_amp, names_from = system, values_from=mean_amp)
blandr.output.text(diff_wide$tr, diff_wide$na, sig.level=0.95)
vignette.chart <- blandr.draw(diff_wide$tr, diff_wide$na, sig.level=0.95)
vignette.chart + theme_classic()
ggsave("BA_meanamp.svg", units="mm", width=76, height=152)

peaks_wide <- pivot_wider(peaks, names_from = system, values_from=c(latency, amplitude))
blandr.output.text(peaks_wide$latency_Trocken, peaks_wide$latency_Nass, sig.level=0.95)
vignette.chart <- blandr.draw(peaks_wide$latency_Trocken, peaks_wide$latency_Nass, sig.level=0.95)
vignette.chart + theme_classic()
ggsave("BA_latency.svg", units="mm", width=37.659, height=76.479)

blandr.output.text(peaks_wide$amplitude_Trocken, peaks_wide$amplitude_Nass, sig.level=0.95)
vignette.chart <- blandr.draw(peaks_wide$amplitude_Trocken, peaks_wide$amplitude_Nass, sig.level=0.95)
vignette.chart + theme_classic()
ggsave("BA_peakamp.svg", units="mm", width=37.659, height=76.479)
