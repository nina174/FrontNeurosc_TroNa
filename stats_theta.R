setwd(...")
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)
library(psych)
library(rstatix)
library(ggrain)
library(stringr)
library(blandr)

theta_tr <- read.csv("theta_TR.csv")
bad <- c(5)
theta_tr <- theta_tr %>%
  filter(!participants %in% bad)

theta_na <- read.csv("theta_NA.csv")
bad <- c(5)
theta_na <- theta_na %>%
  filter(!participants %in% bad)

theta <- merge(theta_tr, theta_na, by = c("participants", "tone"), suffixes = c(".dry", ".wet"))
theta$tone <- as.factor(theta$tone)
theta <- gather(theta, system, amp, amp.dry:amp.wet)

theta <- theta %>%
  mutate_at("system", str_replace, "amp.", "") 
theta$system <- as.factor(theta$system)

ggplot(theta, aes(x=tone, y=amp, fill=tone)) +
  geom_rain(alpha = .5) +
  theme_classic() +
  scale_fill_brewer(palette = 'Dark2') +
  guides(fill = 'none', color = 'none') +
  facet_wrap(~system) 

# anova
# assumptions
theta %>%
  group_by(system, tone) %>%
  identify_outliers(amp)

theta %>%
  group_by(system, tone) %>%
  shapiro_test(amp)

ggqqplot(theta, "amp", ggtheme = theme_bw()) +
  facet_grid(tone ~ system, labeller = "label_both")

res.aov <- anova_test(
  data = theta, dv = amp, wid = participants,
  within = c(tone,system),
  effect.size = "pes" # partial eta squared
)
get_anova_table(res.aov)

# FU tests

pwc <- theta %>%
  group_by(system) %>%
  t_test(amp ~ tone, paired = TRUE, 
         alternative="greater",
         #p.adjust.method = "bonferroni"
         )
pwc

# effect size
ef <- theta %>%
  group_by(system) %>%
  cohens_d(
    amp ~ tone,
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

# FU test systems
diff <- data.frame(
  participants = theta$participants[seq(1, nrow(theta)/2, 2)],
  tone = rep("diff", nrow(theta)/2),
  system = c(rep("dry", nrow(theta)/4), rep("wet", nrow(theta)/4)),
  amp = theta$amp[theta$tone=="dev"] - theta$amp[theta$tone=="std"])
  
describeBy(diff, group = c("system"))

pwc <- diff %>%
  pairwise_t_test(
    amp ~ system, paired = TRUE
  )
pwc

# effect size system
ef <- diff %>%
  cohens_d(
    amp ~ system,
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

###### Bland-Altman
diff$ tone <- NULL
diff_wide <- pivot_wider(diff, names_from = system, values_from=amp)
blandr.output.text(diff_wide$dry, diff_wide$wet, sig.level=0.95)
vignette.chart <- blandr.draw(diff_wide$dry, diff_wide$wet, sig.level=0.95)
vignette.chart + theme_classic()
ggsave("BA_theta.svg", units="mm", width=37.659, height=76.479)


           
