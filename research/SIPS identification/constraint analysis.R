library(tidyverse)
library(plotly)

constraints <- read_csv("COI by Interval 1.csv") %>% 
  mutate(SETTLEMENTDATE = force_tz(SETTLEMENTDATE, tzone = "Australia/Brisbane"),
         doy = yday(SETTLEMENTDATE),
         yr = year(SETTLEMENTDATE),
         type = if_else(grepl("SIP", CONSTRAINTID), "SIPS", "normal"),
         group = if_else(grepl("SIPS", CONSTRAINTID), substr(CONSTRAINTID, 1, nchar(CONSTRAINTID)-5),
                         if_else(grepl("SIP", CONSTRAINTID), substr(CONSTRAINTID, 1, nchar(CONSTRAINTID)-4),
                                 CONSTRAINTID)
                         )
         )

# average number of daily intervals
constraints %>% 
  mutate(moy = month(SETTLEMENTDATE)) %>% 
  group_by(CONSTRAINTID, doy, moy, yr, type) %>% 
  summarise(interval_count = n()) %>% 
  group_by(CONSTRAINTID, moy, yr, type) %>% 
  summarise(num_intervals = mean(interval_count)) %>% 
  ungroup() %>% 
  mutate(date = make_date(year = yr, month = moy, day = 1)) %>% 
  ggplot() +
  geom_line(aes(x = date, y = num_intervals, color = CONSTRAINTID, linetype = type)) +
  facet_wrap(~type, nrow = 2) +
  theme(legend.position = "bottom") +
  theme_minimal()

# monthly average RHS value
constraints %>% 
  mutate(moy = month(SETTLEMENTDATE)) %>% 
  group_by(CONSTRAINTID, moy, yr, type) %>%
  summarise(RHS = mean(RHS)) %>% 
  ungroup() %>% 
  mutate(date = make_date(year = yr, month = moy, day = 1)) %>% 
  ggplot() +
  geom_line(aes(x = date, y = RHS, color = CONSTRAINTID, linetype = type)) +
  facet_wrap(~type, nrow = 2) +
  theme(legend.position = "bottom") +
  theme_minimal()

# constraint swampping and switching for first SIPS period, 2021-2022
constraints %>%
  filter(SETTLEMENTDATE >= "2021-11-01 00:00:00 UTC" & SETTLEMENTDATE < "2022-04-01 09:00:00 UTC") %>% 
  filter(group %in% unique(.[.$type == "SIPS",]$group)) %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y= RHS, color = type)) +
  facet_wrap(~group, scales = "free", ncol = 2) +
  theme_minimal()

# constraint swampping and switching for forth SIPS period, 2024-2025
constraints %>%
  filter(SETTLEMENTDATE >= "2024-11-01 00:00:00 UTC" & SETTLEMENTDATE < "2025-04-01 09:00:00 UTC") %>% 
  filter(group %in% unique(.[.$type == "SIPS",]$group)) %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y= RHS, color = type)) +
  facet_wrap(~group, scales = "free", ncol = 2) +
  theme_minimal()

# constraint swampping and switching for second non-SIPS period, 2023
constraints %>%
  filter(SETTLEMENTDATE >= "2023-04-01 00:00:00 UTC" & SETTLEMENTDATE < "2023-11-01 00:00:00 UTC") %>% 
  filter(group %in% unique(.[.$type == "SIPS",]$group)) %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y= RHS, color = type)) +
  facet_wrap(~group, scales = "free", ncol = 2) +
  theme_minimal()

# RHS timeseries by constraint group (assuming alternative constraint is swamped)
constraints %>% 
  group_by(SETTLEMENTDATE, group) %>% 
  summarise(RHS = min(RHS)) %>% 
  ungroup() %>% 
  filter(RHS <= 10000) %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y = RHS, color = group)) +
  theme_minimal() + 
  theme(legend.position = "bottom") +
  ylim(1000, 3000)

# daily average RHS timeseries by constraint group (assuming alternative constraint is swamped)
constraints %>% 
  filter(grepl("NIL", group) | grepl("SW", group)) %>% 
  group_by(SETTLEMENTDATE, group) %>% 
  summarise(RHS = min(RHS)) %>% 
  ungroup() %>%
  filter(RHS <= 10000) %>% 
  mutate(doy = day(SETTLEMENTDATE),
         moy = month(SETTLEMENTDATE),
         yr = year(SETTLEMENTDATE)) %>% 
  group_by(doy, moy, yr, group) %>% 
  summarise(RHS = mean(RHS)) %>% 
  ungroup() %>%
  mutate(date = make_date(year = yr, month = moy, day = doy)) %>% 
  ggplot() +
  geom_line(aes(x = date, y = RHS, color = group)) +
  theme_minimal() + 
  theme(legend.position = "bottom") +
  ylim(1000, 3000)

# inspect how SIPS constraints swamp/un-swamp collectively
# 2021-22: 2 pairs -- V>>V_NIL_1A/V>>V_NIL_1B, V>>V_NIL_3/V>>V_NIL_4
# 2022-23: 3 pairs -- V>>V_NIL_1A/V>>V_NIL_1B, V>>V_NIL_3/V>>V_NIL_4, V>SW_MSDD1_MSDD2/V>SW_MSDD2_MSDD1
# 2023-24: 2 pairs -- V>>NIL_DDSM_DDSM/V>>NIL_EPTT_DDSM, V>SW_MSDD1_MSDD2/V>SW_MSDD2_MSDD1
# 2024-25: 2 pairs -- V>>NIL_DDSM_DDSM/V>>NIL_EPTT_DDSM, V>SW_MSDD1_MSDD2/V>SW_MSDD2_MSDD1
# Few days 2025: 1 pair -- V>>NIL_DDSM_DDSM/V>>NIL_EPTT_DDSM
temp <- constraints %>% 
  filter(SETTLEMENTDATE >= "2022-11-01 00:00:00" & SETTLEMENTDATE < "2023-04-01 09:00:00") %>% 
  group_by(SETTLEMENTDATE, group) %>% 
  filter(RHS == min(RHS)) %>% 
  ungroup() %>% 
  filter(RHS <= 10000) %>% 
  select(SETTLEMENTDATE, group, type)

temp2 <- tibble(constraint_eqs = unique(temp$group))
denom <- length(unique(temp$SETTLEMENTDATE))

for (i in temp2$constraint_eqs) {
  temp3 <- c()
  for (j in temp2$constraint_eqs) {
    temp3[j] = temp %>% 
      filter(group %in% c(i, j)) %>% 
      group_by(SETTLEMENTDATE) %>% 
      summarise(count = sum(type == "SIPS")) %>% 
      ungroup() %>% 
      filter(if (i != j) {
        count == 2} else {
          count == 1}) %>% 
      nrow(.)/denom
  }
  temp2 <- temp2 %>% 
    mutate(!!i := temp3)
}

# inspect time of day constraint profiles
prd = 2022
constraints %>% 
  filter(SETTLEMENTDATE >= paste0(prd, "-11-01 01:00:00 AEST") & SETTLEMENTDATE < paste0(prd+1, "-04-01 00:00:00 AEST")) %>% 
  # select constraint pairs
  filter(if (prd == 2021) {group %in% c("V>>V_NIL_1A", "V>>V_NIL_3")}
         else if (prd == 2022) {group %in% c("V>>V_NIL_1A", "V>>V_NIL_3", "V>SW_MSDD1_MSDD2")}
         else {group %in% c("V>>NIL_DDSM_DDSM", "V>SW_MSDD1_MSDD2")}) %>% 
  group_by(SETTLEMENTDATE, group) %>% 
  filter(RHS == min(RHS)) %>% 
  ungroup() %>% 
  filter(RHS <= 10000) %>% 
  mutate(time = format(SETTLEMENTDATE, "%H:%M:%S"),
         moy = month(SETTLEMENTDATE, label = TRUE, abbr = TRUE)) %>% 
  group_by(group, time, moy) %>% 
  summarise(SIPS = sum(type == "SIPS")/n()) %>% 
  ungroup() %>% 
  ggplot() +
  geom_bar(aes(x = time, y = SIPS, fill = group), stat = "identity", position = "dodge") +
  facet_wrap(~moy, ncol = 1) +
  theme_minimal() +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5))
  
ic_flows <- read_csv("IC flows by interval.csv") %>% 
  filter(INTERCONNECTORID == "VIC1-NSW1") %>% 
  mutate(doy = yday(SETTLEMENTDATE),
         yr = year(SETTLEMENTDATE))

# percentage of time constraints set import limit
ic_flows %>% 
  group_by(IMPORTGENCONID, yr) %>% 
  summarise(num_intervals = n()) %>% 
  group_by(yr) %>% 
  mutate(perc_intervals = num_intervals/sum(num_intervals)) %>%
  filter(perc_intervals > 0.005) %>% 
  ungroup() %>% 
  arrange(yr, desc(perc_intervals)) %>% 
  ggplot() +
  geom_bar(aes(y = IMPORTGENCONID, x = perc_intervals), stat = "identity") +
  facet_wrap(~yr, scales = "free") +
  theme_minimal()

# percentage of time constraint type sets import limit
ic_flows %>% 
  mutate(type = substr(IMPORTGENCONID, 2, 2)) %>% 
  group_by(type, yr) %>% 
  summarise(num_intervals = n()) %>% 
  group_by(yr) %>% 
  mutate(perc_intervals = num_intervals/sum(num_intervals)) %>%
  ungroup() %>% 
  arrange(yr, desc(perc_intervals)) %>% 
  ggplot() +
  geom_bar(aes(y = type, x = perc_intervals), stat = "identity") +
  facet_wrap(~yr, scales = "free") +
  theme_minimal()

# average daily hours VNI import is binding
ic_flows %>% 
  mutate(moy = month(SETTLEMENTDATE)) %>% 
  group_by(doy, yr, moy) %>% 
  summarise(binding_import_intervals = sum(LOCALLY_CONSTRAINED_IMPORT > 0)) %>% 
  mutate(binding_import_hours = binding_import_intervals/12) %>% 
  group_by(moy, yr) %>% 
  summarise(binding_import_hours = mean(binding_import_hours)) %>% 
  ungroup() %>% 
  mutate(date = make_date(year = yr, month = moy, day = 1)) %>% 
  ggplot() +
  geom_bar(aes(x = date, y = binding_import_hours), stat = "identity") +
  theme_minimal()

# distribution of local import prices when VNI is binding
ic_flows %>% 
  mutate(moy = month(SETTLEMENTDATE)) %>% 
  filter(LOCALLY_CONSTRAINED_IMPORT > 0) %>% 
  group_by(moy, yr) %>% 
  mutate(average_import_price = mean(LOCAL_PRICE_ADJUSTMENT_IMPORT)) %>% 
  ungroup() %>% 
  mutate(date = make_date(year = yr, month = moy, day = 1)) %>% 
  ggplot() +
  geom_boxplot(aes(x = date, y = LOCAL_PRICE_ADJUSTMENT_IMPORT, group = date)) +
  geom_line(aes(x = date, y = average_import_price), color = "red", linewidth = 2) +
  ylim(0, 1000) +
  theme_minimal()


vbb <- read_csv("VBB dispatch.csv") %>% 
  mutate(dom = day(SETTLEMENTDATE),
         moy = month(SETTLEMENTDATE),
         yr = year(SETTLEMENTDATE))

# look at maximum daily availability
vbb %>% 
  filter(DUID %in% c("VBB1", "VBBG1")) %>% 
  group_by(dom, moy, yr) %>% 
  summarise(AVAILABILITY = max(AVAILABILITY)) %>% 
  ungroup() %>% 
  mutate(date = make_date(year = yr, month = moy, day = dom)) %>% 
  ggplot() +
  geom_line(aes(x = date, y = AVAILABILITY)) +
  theme_minimal()

# vbb energy availability versus constraint type
constraints %>% 
  mutate(moy = month(SETTLEMENTDATE)) %>% 
  filter( moy %in% c(11, 12, 1, 2, 3) & 
           group %in% c("V>>V_NIL_1A", "V>>V_NIL_3", "V>>NIL_DDSM_DDSM", "V>SW_MSDD1_MSDD2")) %>%
  group_by(SETTLEMENTDATE, group, INTERVENTION) %>% 
  filter(RHS == min(RHS)) %>% 
  ungroup() %>% 
  filter(RHS <= 10000) %>% 
  left_join(
    select(
      filter(vbb, DUID %in% c("VBB1", "VBBG1")),
      SETTLEMENTDATE, INTERVENTION, DUID, AVAILABILITY), 
    by = c("SETTLEMENTDATE", "INTERVENTION")) %>% 
  ggplot() +
  geom_boxplot(aes(x = group, y = AVAILABILITY, color = type)) +
  theme_minimal()

# vbb energy dispatch versus constraint type
constraints %>% 
  mutate(moy = month(SETTLEMENTDATE)) %>% 
  filter( moy %in% c(11, 12, 1, 2, 3) & 
            group %in% c("V>>V_NIL_1A", "V>>V_NIL_3", "V>>NIL_DDSM_DDSM", "V>SW_MSDD1_MSDD2")) %>%
  group_by(SETTLEMENTDATE, group, INTERVENTION) %>% 
  filter(RHS == min(RHS)) %>% 
  ungroup() %>% 
  filter(RHS <= 10000) %>% 
  left_join(
    select(
      filter(vbb, DUID %in% c("VBB1", "VBBG1")),
      SETTLEMENTDATE, INTERVENTION, DUID, TOTALCLEARED), 
    by = c("SETTLEMENTDATE", "INTERVENTION")) %>% 
  ggplot() +
  geom_boxplot(aes(x = group, y = TOTALCLEARED, color = type)) +
  theme_minimal()





