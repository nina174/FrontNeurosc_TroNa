###############################################################################
###################### Statistical analyses ###################################
####################### TRONA resting-state ###################################
######################### Nina Ehrhardt #######################################
###############################################################################

setwd("...")

library(tidyverse)
library(readxl)
library(rstatix)
library(rempsyc)
library(ggrain)
library(blandr)
library(ggcorrplot)
library(flextable)
library(officer)
library(patchwork)

##### prepare dataframes #####

alpha <- read_excel("Alpha_results.xlsx")
peak_freq <- alpha$peak_freq
power <- alpha$alpha1_power + alpha$alpha2_power
alpha <- alpha %>%
  rename(aec=`AEC-c`) %>%
  select(sub_id, aec, PLI, WPLI, MST_Diam, 
         MST_Kappa, MST_Leaf, MST_Teff, MST_Th, MST_degree) %>%
  cbind(power) %>%
  separate(sub_id, c("id", "eeg")) %>%
  mutate(eeg=as.factor(eeg)) %>%
  mutate(freq=as.factor("alpha"))

beta <- read_excel("Beta_results.xlsx")
beta <- beta %>%
  rename(power = beta_power, aec=`AEC-c`) %>%
  select(sub_id, aec, PLI, WPLI, power, MST_Diam, 
         MST_Kappa, MST_Leaf, MST_Teff, MST_Th, MST_degree) %>%
  separate(sub_id, c("id", "eeg")) %>%
  mutate(eeg=as.factor(eeg)) %>%
  mutate(freq=as.factor("beta"))

delta <- read_excel("Delta_results.xlsx")
delta <- delta %>%
  rename(power = delta_power, aec=`AEC-c`) %>%
  select(sub_id, aec, PLI, WPLI, power, MST_Diam, 
         MST_Kappa, MST_Leaf, MST_Teff, MST_Th, MST_degree) %>%
  separate(sub_id, c("id", "eeg")) %>%
  mutate(eeg=as.factor(eeg)) %>%
  mutate(freq=as.factor("delta"))

theta <- read_excel("Theta_results.xlsx")
theta <- theta %>%
  rename(power = theta_power, aec=`AEC-c`) %>%
  select(sub_id, aec, PLI, WPLI, power, MST_Diam, 
         MST_Kappa, MST_Leaf, MST_Teff, MST_Th, MST_degree) %>%
  separate(sub_id, c("id", "eeg")) %>%
  mutate(eeg=as.factor(eeg)) %>%
  mutate(freq=as.factor("theta"))

dat <- rbind(alpha, beta, delta, theta)

dat <- dat[dat["id"] != "1",] # because no TR data for participant one


####### Stats PLI and MST-Diam ######

pli_list <- list()

for(level in levels(dat$freq)){
  pli <- subset(dat[c("id", "eeg", "PLI", "freq")], freq==level)
  pli <- pivot_wider(pli, names_from = eeg, values_from = PLI)
  pli <- na.omit(pli)
  print(level)
  blandr.output.text(pli$TR, pli$`NA`, sig.level=0.95)
  vignette.chart <- blandr.draw(pli$TR, pli$`NA`, sig.level=0.95)
  name <- paste0("PLI ", level)
  p <- vignette.chart + theme_classic() + ggtitle(level) + 
    xlab("Means dry and wet") + ylab("Differences (dry-wet)") 
  # +
    # xlim(0.095, 0.31) + ylim(-0.1, 0.11)
  pli_list[[level]] <-  p
  f_name <- paste0("BA_pli_", level, ".jpg")
  # ggsave(f_name, units="mm", width=76, height=152)
  
}

pli_plots <- wrap_plots(pli_list, ncol = 2) + 
  plot_layout(axis_titles = "collect") + 
  plot_annotation(title = "PLI")
pli_plots
# ggsave("BA_PLI_allplots.jpg", units="mm", width=100, height = 150)

mst_list <- list()

for(level in levels(dat$freq)){
  mst_diam <- subset(dat[c("id", "eeg", "MST_Diam", "freq")], freq==level)
  mst_diam <- pivot_wider(mst_diam, names_from = eeg, values_from = MST_Diam)
  mst_diam <- na.omit(mst_diam)
  print(level)
  blandr.output.text(mst_diam$TR, mst_diam$`NA`, sig.level=0.95)
  vignette.chart <- blandr.draw(mst_diam$TR, mst_diam$`NA`, sig.level=0.95)
  p <- vignette.chart + theme_classic() + ggtitle(level) +
    xlab("Means dry and wet") + ylab("Differences (dry-wet)") +
    xlim(0.32, 0.45) + ylim(-0.15, 0.16)
  mst_list[[level]] <-  p
  f_name <- paste0("BA_mst_diam_", level, ".jpg")
  # ggsave(f_name, units="mm", width=76, height=152)
  
}

mst_plots <- wrap_plots(mst_list, ncol = 2) + 
  plot_layout(axis_titles = "collect") + 
  plot_annotation(title = "MST-Diameter")
mst_plots

all_plots <- pli_plots / mst_plots 
all_plots

plot_list <- append(pli_list, mst_list)

all_plots <- wrap_plots(plot_list, ncol = 4) +
  plot_layout(axis_titles = "collect")
all_plots
ggsave("BA_connectivity_allplots.svg", units="mm", width=200, height = 150)


####### All measures for Supplements #####

dat_long <- pivot_longer(dat, cols = 3:11)

rm(stats.test)
set_flextable_defaults(font.size = 12, theme_fun = theme_vanilla)
### TO DO: add effect size

for(level in levels(dat_long$freq)) {
  tmp <- subset(dat_long, freq==level)
  stat.test <- tmp %>%
  group_by(name) %>%
  wilcox_test(value ~ eeg, paired = TRUE) %>%
  # adjust_pvalue(method="bonferroni") %>%
  add_significance()
  
  ef <- tmp %>%
    group_by(name) %>%
    cohens_d(value ~ eeg, paired = TRUE) %>%
    select(name, effsize, magnitude)

  stat.test <- merge(stat.test, ef, by = "name")
  
  
  stat.test$freq <- rep(level, nrow(stat.test))
  
  if (exists("stats.test")) {
    stats.test <- rbind(stats.test, stat.test)
    } else {
      stats.test <- stat.test
    }
  
}



rm(descrs)
for(level in levels(dat_long$freq)) {
  tmp <- subset(dat_long, freq==level)
  descr <- tmp %>%
    group_by(name, eeg) %>%
    summarise(mean=mean(value), sd=sd(value))
  
  descr$freq <- rep(level, nrow(descr))
  
  if (exists("descrs")) {
    descrs <- rbind(descrs, descr)
  } else {
    descrs <- descr
  }
}

descrs <- pivot_wider(descrs, names_from = eeg, values_from = c(mean,sd))

stats_table <- merge(stats.test, descrs, by = c("name", "freq"))
stats_table <- stats_table %>% 
  select(freq, name, n1, n2, mean_NA, sd_NA, mean_TR, sd_TR, statistic, p, effsize, magnitude) %>% 
  # select(freq, name, n1, n2, mean_NA, sd_NA, mean_TR, sd_TR, statistic, df, p, p.adj, p.adj.signif) %>%
  arrange(freq) %>% 
  rename(NA.M = mean_NA, NA.SD = sd_NA, TR.M = mean_TR, TR.SD = sd_TR)
ft <- nice_table(stats_table, separate.header = T)
ft <- add_footer_lines(ft, "Notes.")
ft <- set_caption(ft, caption = "Comparison of connectivity measures between wet and dry EEG")
ft

# Save in Word
sect_properties <- prop_section(page_size(orient = "landscape"))

flextable::save_as_docx(ft, path = "t-tests_wilcoxon_n32.docx", pr_section = sect_properties)

####### Plots #######

# dat[c("id", "eeg", "freq")] = NULL
# corr <- cor(dat) 
# 
# ggcorrplot(corr, hc.order=TRUE, type="upper", lab = FALSE, 
#            ggtheme = ggplot2::theme_minimal,
#            outline.color = "white")
# 
# dat <- rbind(alpha, beta, delta, theta)
# dat <- dat %>%
#   filter(id %in% subs)

plot_for_loop <- function(df, x_var, y_var) {
  
  ggplot(df, aes(x = .data[[x_var]], y = .data[[y_var]], fill = .data[[x_var]])) + 
    facet_wrap(vars(freq), ncol = 4) +
    geom_rain(alpha = .5) +
    theme_classic() +
    theme(axis.title.x = element_blank()) +
    scale_fill_brewer(palette = 'Dark2') +
    guides(fill = 'none', color = 'none')
}
dat$eeg <- factor(dat$eeg, labels = c("wet EEG", "dry EEG"))
plot_list <- colnames(dat)[-c(1,2,12)] %>% 
  map( ~ plot_for_loop(dat, colnames(dat)[2], .x))

plot_list[1:10]

# Combine all plots

all_plots <- plot_grid(plotlist = plot_list,
          ncol = 3)
all_plots

ggsave("connectivity_plots_n32.svg", width = 550, height = 300, units = "mm")
