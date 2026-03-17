library(tidyverse)

pricebands <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/biddayoffer_d.csv")

init <- pricebands %>% 
  filter(BIDTYPE == "ENERGY" & SETTLEMENTDATE >= "2021-12-08")

# - SIPS price bands almost always remain the same
# - Non-SIPS price bands almost always remain the same
# - SIPS and non-SIPS price bands also almost always remain the same, except when something shifts (MPC) or some adjustment to trading
init %>% 
  filter(DIRECTION == "GEN") %>% 
  pivot_longer(cols = PRICEBAND1:PRICEBAND10, names_to = "band", values_to = "price") %>% 
  mutate(yr = year(SETTLEMENTDATE),
         period = case_when((month(SETTLEMENTDATE) >= 11 & yr == 2021) | (month(SETTLEMENTDATE) < 4 & yr == 2022) ~ "SIPS1",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2022) | (month(SETTLEMENTDATE) < 4 & yr == 2023) ~ "SIPS2",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2023) | (month(SETTLEMENTDATE) < 4 & yr == 2024) ~ "SIPS3",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2024) | (month(SETTLEMENTDATE) < 4 & yr == 2025) ~ "SIPS4",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2025) | (month(SETTLEMENTDATE) < 4 & yr == 2026) ~ "SIPS5",
                            month(SETTLEMENTDATE) < 11 & yr == 2022 ~ "N1",
                            month(SETTLEMENTDATE) < 11 & yr == 2023 ~ "N2",
                            month(SETTLEMENTDATE) < 11 & yr == 2024 ~ "N3",
                            month(SETTLEMENTDATE) < 11 & yr == 2025 ~ "N4",
                            month(SETTLEMENTDATE) < 11 & yr == 2026 ~ "N5")) %>% 
  filter(period != "Normal") %>% 
  ggplot() +
  geom_boxplot(aes(x = band, y = price, group = band)) +
  facet_wrap(~period)

init %>% 
  filter(DIRECTION == "LOAD") %>% 
  pivot_longer(cols = PRICEBAND1:PRICEBAND10, names_to = "band", values_to = "price") %>% 
  mutate(yr = year(SETTLEMENTDATE),
         period = case_when((month(SETTLEMENTDATE) >= 11 & yr == 2021) | (month(SETTLEMENTDATE) < 4 & yr == 2022) ~ "SIPS1",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2022) | (month(SETTLEMENTDATE) < 4 & yr == 2023) ~ "SIPS2",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2023) | (month(SETTLEMENTDATE) < 4 & yr == 2024) ~ "SIPS3",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2024) | (month(SETTLEMENTDATE) < 4 & yr == 2025) ~ "SIPS4",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2025) | (month(SETTLEMENTDATE) < 4 & yr == 2026) ~ "SIPS5",
                            month(SETTLEMENTDATE) < 11 & yr == 2022 ~ "N1",
                            month(SETTLEMENTDATE) < 11 & yr == 2023 ~ "N2",
                            month(SETTLEMENTDATE) < 11 & yr == 2024 ~ "N3",
                            month(SETTLEMENTDATE) < 11 & yr == 2025 ~ "N4",
                            month(SETTLEMENTDATE) < 11 & yr == 2026 ~ "N5")) %>% 
  filter(period != "Normal") %>% 
  ggplot() +
  geom_boxplot(aes(x = band, y = price, group = band)) +
  facet_wrap(~period)

pricebands %>% 
  filter(BIDTYPE == "RAISE6SEC") %>% 
  pivot_longer(cols = PRICEBAND1:PRICEBAND10, names_to = "band", values_to = "price") %>% 
  mutate(yr = year(SETTLEMENTDATE),
         period = case_when((month(SETTLEMENTDATE) >= 11 & yr == 2021) | (month(SETTLEMENTDATE) < 4 & yr == 2022) ~ "SIPS1",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2022) | (month(SETTLEMENTDATE) < 4 & yr == 2023) ~ "SIPS2",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2023) | (month(SETTLEMENTDATE) < 4 & yr == 2024) ~ "SIPS3",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2024) | (month(SETTLEMENTDATE) < 4 & yr == 2025) ~ "SIPS4",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2025) | (month(SETTLEMENTDATE) < 4 & yr == 2026) ~ "SIPS5",
                            month(SETTLEMENTDATE) < 11 & yr == 2022 ~ "N1",
                            month(SETTLEMENTDATE) < 11 & yr == 2023 ~ "N2",
                            month(SETTLEMENTDATE) < 11 & yr == 2024 ~ "N3",
                            month(SETTLEMENTDATE) < 11 & yr == 2025 ~ "N4",
                            month(SETTLEMENTDATE) < 11 & yr == 2026 ~ "N5")) %>% 
  filter(period != "Normal") %>% 
  ggplot() +
  geom_boxplot(aes(x = band, y = price, group = band)) +
  facet_wrap(~period)

capacitybands <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_1.csv") %>% 
  rbind(read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_2.csv")) %>% 
  rbind(read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_3.csv")) %>% 
  rbind(read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_4.csv"))

capacitybands %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "LOWERREG" & DIRECTION == "GEN") %>% 
  mutate(yr = year(SETTLEMENTDATE),
         period = case_when((month(SETTLEMENTDATE) >= 11 & yr == 2021) | (month(SETTLEMENTDATE) < 4 & yr == 2022) ~ "SIPS1",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2022) | (month(SETTLEMENTDATE) < 4 & yr == 2023) ~ "SIPS2",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2023) | (month(SETTLEMENTDATE) < 4 & yr == 2024) ~ "SIPS3",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2024) | (month(SETTLEMENTDATE) < 4 & yr == 2025) ~ "SIPS4",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2025) | (month(SETTLEMENTDATE) < 4 & yr == 2026) ~ "SIPS5")) %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = MAXAVAIL, group = PERIODID)) +
  facet_wrap(~period)

capacitybands %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "RAISEREG" & DIRECTION == "GEN") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  mutate(capacity_prop = capacity/MAXAVAIL) %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = capacity, group = PERIODID), outliers = FALSE, whisker.linewidth = 0) +
  facet_wrap(~band)

capacitybands %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "ENERGY" & DIRECTION == "LOAD") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  filter(band %in% c("BANDAVAIL1", "BANDAVAIL2", "BANDAVAIL4")) %>% 
  group_by(band, PERIODID) %>% 
  mutate(capacity = mean(capacity)) %>% 
  ungroup() %>% 
  mutate(yr = year(SETTLEMENTDATE),
         period = case_when((month(SETTLEMENTDATE) >= 11 & yr == 2021) | (month(SETTLEMENTDATE) < 4 & yr == 2022) ~ "SIPS1",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2022) | (month(SETTLEMENTDATE) < 4 & yr == 2023) ~ "SIPS2",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2023) | (month(SETTLEMENTDATE) < 4 & yr == 2024) ~ "SIPS3",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2024) | (month(SETTLEMENTDATE) < 4 & yr == 2025) ~ "SIPS4",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2025) | (month(SETTLEMENTDATE) < 4 & yr == 2026) ~ "SIPS5")) %>% 
  ggplot() +
  geom_line(aes(x = PERIODID, y = capacity, colour = band)) +
  facet_wrap(~period)

capacitybands %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "RAISEREG" & DIRECTION == "GEN") %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = MAXAVAIL, group = PERIODID))

capacitybands %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "RAISEREG") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = capacity, group = PERIODID), outliers = FALSE, whisker.linewidth = 0) +
  facet_wrap(~band)


capacitybands_nonsips <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_1b.csv") %>% 
  rbind(read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_2b.csv")) %>% 
  rbind(read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/bidperoffer_d_3b.csv"))

capacitybands_nonsips %>% 
  filter(SETTLEMENTDATE >= "2022-04-01") %>% 
  filter(BIDTYPE == "ENERGY" & DIRECTION == "LOAD") %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = MAXAVAIL, group = PERIODID))

capacitybands_nonsips %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "RAISE6SEC" & DIRECTION == "GEN") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  mutate(capacity_prop = capacity/MAXAVAIL) %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = capacity, group = PERIODID), outliers = FALSE, whisker.linewidth = 0) +
  facet_wrap(~band)

capacitybands_nonsips %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "RAISEREG" & DIRECTION == "GEN") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  filter(band %in% c("BANDAVAIL1", "BANDAVAIL8", "BANDAVAIL10")) %>% 
  group_by(band, PERIODID) %>% 
  mutate(capacity = mean(capacity)) %>% 
  ggplot() +
  geom_line(aes(x = PERIODID, y = capacity, colour = band))

# bid-time delta to settlement time - no pattern
capacitybands_nonsips %>% 
  filter(BIDTYPE == "ENERGY") %>% 
  mutate(bid_gap = INTERVAL_DATETIME - LASTCHANGED) %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = bid_gap, group = PERIODID), outliers = FALSE) +
  facet_wrap(~DIRECTION)

# pre-dispatch prices vs band allocation - nothing conclusive
predispatch <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/p5min_regionsolution.csv")

predispatch <- predispatch %>% 
  group_by(INTERVAL_DATETIME) %>% 
  filter(RUN_DATETIME == max(RUN_DATETIME)) %>% 
  ungroup()

capacitybands %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "ENERGY" & DIRECTION == "LOAD") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  filter(band %in% c("BANDAVAIL2", "BANDAVAIL8")) %>% 
  left_join(predispatch, by = "INTERVAL_DATETIME") %>% 
  filter(MAXAVAIL > 0) %>% 
  ggplot() +
  geom_point(aes(x = capacity, y = RRP), alpha = 0.1) +
  geom_smooth(aes(x = capacity, y = RRP)) +
  facet_wrap(~band) +
  xlim(0, 50) +
  ylim(0, 300)

capacitybands_nonsips %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "ENERGY" & DIRECTION == "LOAD") %>% 
  pivot_longer(cols = BANDAVAIL1:BANDAVAIL10, names_to = "band", values_to = "capacity") %>% 
  filter(band %in% c("BANDAVAIL4")) %>% 
  left_join(predispatch, by = "INTERVAL_DATETIME") %>% 
  filter(MAXAVAIL > 0 & capacity > 0) %>% 
  ggplot() +
  geom_point(aes(y = capacity, x = RRP), alpha = 0.1) +
  geom_smooth(aes(y = capacity, x = RRP)) +
  facet_wrap(~band) +
  ylim(0, 250) +
  xlim(-100, 100)


# dispatchload
dispatchload_orig <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchload.csv")

dispatchload_orig <- dispatchload_orig %>% 
  mutate(yr = year(SETTLEMENTDATE),
         period = case_when((month(SETTLEMENTDATE) >= 11 & yr == 2021) | (month(SETTLEMENTDATE) < 4 & yr == 2022) ~ "P1",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2022) | (month(SETTLEMENTDATE) < 4 & yr == 2023) ~ "P2",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2023) | (month(SETTLEMENTDATE) < 4 & yr == 2024) ~ "P3",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2024) | (month(SETTLEMENTDATE) < 4 & yr == 2025) ~ "P4",
                            (month(SETTLEMENTDATE) >= 11 & yr == 2025) | (month(SETTLEMENTDATE) < 4 & yr == 2026) ~ "P5",
                            month(SETTLEMENTDATE) < 11 & yr == 2022 ~ "P1b",
                            month(SETTLEMENTDATE) < 11 & yr == 2023 ~ "P2b",
                            month(SETTLEMENTDATE) < 11 & yr == 2024 ~ "P3b",
                            month(SETTLEMENTDATE) < 11 & yr == 2025 ~ "P4b",
                            month(SETTLEMENTDATE) < 11 & yr == 2026 ~ "P5b")) %>% 
  arrange(SETTLEMENTDATE, DUID) %>% 
  group_by(DUID) %>% 
  mutate(INITIALMW = lead(INITIALMW, n = 1)) %>% 
  ungroup() %>% 
  mutate(BIDTYPE = case_when(DUID == "VBBG1" ~ "GEN",
                             DUID == "VBBL1" ~ "LOAD",
                             DUID == "VBB1" & INITIALMW >= 0 ~ "GEN",
                             DUID == "VBB1" & INITIALMW < 0 ~ "LOAD"))

temp <- dispatchload_orig %>% 
  select(-BIDTYPE, -TOTALCLEARED) %>% 
  pivot_longer(cols = c("LOWER5MIN", "LOWER60SEC", "LOWER6SEC","LOWER1SEC",
                        "RAISE5MIN", "RAISE60SEC", "RAISE6SEC", "RAISE1SEC",
                        "RAISEREG", "LOWERREG"), names_to = "BIDTYPE", values_to = "TOTALCLEARED")

dispatchload <- dispatchload_orig %>% 
  select(-c("LOWER5MIN", "LOWER60SEC", "LOWER6SEC", "LOWER1SEC",
            "RAISE5MIN", "RAISE60SEC", "RAISE6SEC", "RAISE1SEC",
            "RAISEREG", "LOWERREG")) %>% 
  rbind(temp) %>% 
  arrange(SETTLEMENTDATE)  %>% 
  mutate(TOTALCLEARED = abs(TOTALCLEARED))

dispatchload %>% 
  filter(BIDTYPE == "LOAD") %>% 
  group_by(SETTLEMENTDATE) %>% 
  mutate(TOTALCLEARED = sum(TOTALCLEARED)) %>% 
  filter(TOTALCLEARED > 0) %>% 
  ungroup() %>% 
  ggplot() +
  geom_boxplot(aes(x = period, y = TOTALCLEARED, group = period))

period_index <- capacitybands %>% mutate(time = substr(INTERVAL_DATETIME, 12, 20)) %>%  distinct(PERIODID, time)

dispatchload %>% 
  filter(BIDTYPE == "LOAD") %>% 
  group_by(SETTLEMENTDATE) %>% 
  mutate(TOTALCLEARED = sum(TOTALCLEARED)) %>% 
  ungroup() %>% 
  mutate(time = substr(SETTLEMENTDATE, 12, 20)) %>% 
  left_join(period_index, by = "time") %>% 
#  filter(TOTALCLEARED > 0) %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = TOTALCLEARED, group = PERIODID), outlier.alpha = 0.1, whisker.linewidth = 0) +
  facet_wrap(~period, ncol = 2)
  
# pre-dispatch residual demand elasticity
pricesensitivities <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/p5min_pricesensitivities.csv") %>% 
  group_by(INTERVAL_DATETIME) %>% 
  filter(RUN_DATETIME == max(RUN_DATETIME))

predispatch2 <- predispatch %>% 
  left_join(pricesensitivities, by = c("INTERVAL_DATETIME", "REGIONID", "RUN_DATETIME")) %>% 
  mutate(pdem_el = (RRP4 - RRP)/150,
         ndem_el = (RRP - RRP5)/150)

dispatchload %>% 
  filter(BIDTYPE == "GEN" & substr(period, 3, 3) == "b") %>%
  mutate(TOTALCLEARED = abs(TOTALCLEARED)) %>% 
  left_join(predispatch2, by = c("SETTLEMENTDATE"="INTERVAL_DATETIME")) %>% 
  filter(TOTALCLEARED > 0) %>% 
  ggplot() +
  geom_point(aes(x = ndem_el, y = TOTALCLEARED), alpha = 0.1) +
  geom_smooth(aes(x = ndem_el, y = TOTALCLEARED)) +
  xlim(0, 1.5)

# load is often unconstrained, let's compare daily distribution of energy dispatch vs charge
dispatchload_orig %>%
  mutate(INITIALMW = abs(INITIALMW),
         doy = yday(SETTLEMENTDATE),
         yr = year(SETTLEMENTDATE)) %>% 
  group_by(doy, yr, period, BIDTYPE) %>% 
  summarise(daily_energy = sum(INITIALMW)/12) %>% 
  ungroup() %>%
  ggplot() +
  geom_boxplot(aes(y = daily_energy, x = BIDTYPE, group = BIDTYPE)) +
  facet_wrap(~period)
  
dispatchload_orig %>% 
  arrange(SETTLEMENTDATE, DUID) %>% 
  mutate(INITIALMW = abs(INITIALMW),
         doy = yday(SETTLEMENTDATE),
         yr = year(SETTLEMENTDATE)) %>% 
  group_by(period, BIDTYPE) %>% 
  summarise(daily_energy = sum(INITIALMW)/12) %>% 
  ungroup() %>%
  pivot_wider(names_from = BIDTYPE, values_from = daily_energy) %>% 
  mutate(RTE = LOAD/GEN) %>% 
  ggplot() +
  geom_point(aes(y = RTE, x = period)) +
  geom_hline(aes(yintercept = 1)) + 
  geom_hline(aes(yintercept = 1/0.85))

# total energy traded per period - load
dispatchload_orig %>% 
  mutate(INITIALMW = case_when(DUID == "VBBL1" ~ -1*INITIALMW,
                               TRUE ~ INITIALMW)) %>% 
  group_by(SETTLEMENTDATE, period) %>% 
  summarise(INITIALMW = sum(INITIALMW)) %>% 
  ungroup() %>% 
  mutate(INITIALMW = 0.5*(INITIALMW + lag(INITIALMW, n = 1, default = 0))) %>% 
  filter(INITIALMW < 0) %>% 
  group_by(period) %>% 
  summarise(cycles = sum(abs(INITIALMW))/12/450*sqrt(0.85)) %>% 
  ungroup() %>% 
  mutate(days = case_when(period == "P1" ~ 114,
                          substr(period, 3, 3) == "b" ~ 214,
                          TRUE ~ 151)) %>% 
  ggplot() +
  geom_bar(aes(x = period, y = cycles), stat = "identity") +
  geom_point(aes(x = period, y = days))

dispatchload_orig %>% 
  mutate(INITIALMW = case_when(DUID == "VBBL1" ~ -1*INITIALMW,
                               TRUE ~ INITIALMW)) %>% 
  group_by(SETTLEMENTDATE, period) %>% 
  summarise(INITIALMW = sum(INITIALMW)) %>% 
  ungroup() %>% 
  mutate(INITIALMW = 0.5*(INITIALMW + lag(INITIALMW, n = 1, default = 0))) %>% 
  filter(INITIALMW > 0) %>% 
  group_by(period) %>% 
  summarise(cycles = sum(abs(INITIALMW))/12/450/sqrt(0.85)) %>% 
  ungroup() %>% 
  mutate(days = case_when(period == "P1" ~ 114,
                          substr(period, 3, 3) == "b" ~ 214,
                          TRUE ~ 151)) %>% 
  ggplot() +
  geom_bar(aes(x = period, y = cycles), stat = "identity") +
  geom_point(aes(x = period, y = days))
  
  
# dispatch cycles
dispatchload_orig %>% 
  arrange(SETTLEMENTDATE, DUID) %>% 
  filter(BIDTYPE == "GEN") %>% 
  group_by(period) %>% 
  summarise(total_cycles = sum(INITIALMW, na.rm = TRUE)/12/450,
            number_of_days = as.numeric(max(SETTLEMENTDATE) - min(SETTLEMENTDATE))) %>% 
  ungroup() %>%
  pivot_longer(cols = total_cycles:number_of_days, names_to = "field", values_to = "values") %>% 
  ggplot() +
  geom_bar(aes(x = period, y = values, fill = field), stat = "identity", position = "dodge")

# delta SOC versus initial MW
dispatchload_orig %>%
  filter(DUID == "VBB1" & SETTLEMENTDATE > "2024-10-02 21:00:00") %>%  #2024-10-02 11:00:00
  right_join(tibble(SETTLEMENTDATE = seq(from = ymd_hms("2024-10-02 11:05:00"), to = max(dispatchload_orig$SETTLEMENTDATE), by = "5 min")),
             by = "SETTLEMENTDATE") %>% 
  mutate(CALC_INITIALMW = -1*(lead(INITIAL_ENERGY_STORAGE) - INITIAL_ENERGY_STORAGE)*12,
         INITIALMW_MIDPOINT = 0.5*(lag(INITIALMW) + INITIALMW),
         INITIALMW_MIDPOINT = case_when(INITIALMW_MIDPOINT < 0 ~ INITIALMW_MIDPOINT*sqrt(0.9),
                                        INITIALMW_MIDPOINT >= 0 ~ INITIALMW_MIDPOINT/sqrt(0.9))) %>% 
  #filter(RAISEREG == 0 & LOWERREG == 0) %>% 
  ggplot() +
  geom_point(aes(x = CALC_INITIALMW,
                 y = INITIALMW_MIDPOINT), alpha = 0.1) +
  geom_abline(aes(intercept = 0, slope = 1), color = "blue") +
  geom_smooth(aes(x = CALC_INITIALMW,
                  y = INITIALMW_MIDPOINT)) +
  xlim(-300, 300) +
  ylim(-300, 300)

# inspect the same for TOTALCLEARED midpoint + util rate * REG
dispatchload_orig %>%
  filter(DUID == "VBB1" & SETTLEMENTDATE > "2024-10-02 21:00:00") %>%  #2024-10-02 11:00:00
  right_join(tibble(SETTLEMENTDATE = seq(from = ymd_hms("2024-10-02 11:05:00"), to = max(dispatchload_orig$SETTLEMENTDATE), by = "5 min")),
             by = "SETTLEMENTDATE") %>% 
  mutate(CALC_INITIALMW = -1*(lead(INITIAL_ENERGY_STORAGE) - INITIAL_ENERGY_STORAGE)*12,
         TOTALCLEARED_MIDPOINT = 0.5*(lag(TOTALCLEARED) + TOTALCLEARED) + 0.18 * RAISEREG - 0.08 * LOWERREG,
         TOTALCLEARED_ADJ = TOTALCLEARED + 0.18 * RAISEREG - 0.08 * LOWERREG) %>% 
  ggplot() +
  geom_point(aes(x = CALC_INITIALMW,
                 y = TOTALCLEARED_ADJ), alpha = 0.1) +
  geom_abline(aes(intercept = 0, slope = 1), color = "blue") +
  xlim(-300, 300) +
  ylim(-300, 300)

# rolling SOC for INITIAL_ENERGY_STORAGE
dispatchload_orig %>%
  select(SETTLEMENTDATE, DUID, INITIAL_ENERGY_STORAGE, INITIALMW) %>% 
  filter(DUID == "VBB1" & SETTLEMENTDATE > "2024-10-02 21:00:00") %>%  #2024-10-02 11:00:00
  right_join(tibble(SETTLEMENTDATE = seq(from = ymd_hms("2024-10-02 11:05:00"), to = max(dispatchload_orig$SETTLEMENTDATE), by = "5 min")),
             by = "SETTLEMENTDATE") %>% 
  mutate(CALC_INITIALMW = -1*(lead(INITIAL_ENERGY_STORAGE) - INITIAL_ENERGY_STORAGE)*12,
         INITIALMW_MIDPOINT = 0.5*(lag(INITIALMW, default = 0) + INITIALMW),
         INITIALMW_MIDPOINT_SOC = case_when(INITIALMW_MIDPOINT < 0 ~ -1*INITIALMW_MIDPOINT*sqrt(0.8)/12,
                                            INITIALMW_MIDPOINT >= 0 ~ -1*INITIALMW_MIDPOINT/sqrt(0.8)/12),
         soc = cumsum(INITIALMW_MIDPOINT_SOC) + INITIAL_ENERGY_STORAGE[1]) %>%
  pivot_longer(cols = c(soc, INITIAL_ENERGY_STORAGE), names_to = "series", values_to = "value") %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y = value, color = series))
  
# calculate rolling SOC from dispatchload
dispatchload_orig %>% 
  group_by(DUID) %>% 
  mutate(INITIALMW_MIDPOINT = 0.5*(lag(INITIALMW, default = 0) + INITIALMW)) %>% 
  ungroup() %>% 
  mutate(INITIALMW_MIDPOINT = case_when(DUID == "VBBL1" ~ INITIALMW_MIDPOINT*sqrt(0.85),
                                        DUID == "VBB1" & INITIALMW_MIDPOINT < 0 ~ -1*INITIALMW_MIDPOINT*sqrt(0.85),
                                        DUID == "VBBG1" | INITIALMW_MIDPOINT >= 0 ~ -1*INITIALMW_MIDPOINT/sqrt(0.85))) %>% 
  group_by(SETTLEMENTDATE, period) %>% 
  summarise(mw_delta = sum(INITIALMW_MIDPOINT, na.rm = TRUE),
            soc_delta = mw_delta/12) %>% 
  group_by(period) %>%
  mutate(soc = cumsum(soc_delta)) %>%  
  ungroup() %>% 
  filter(period == "P1b") %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y = soc)) +
  geom_hline(aes(yintercept = 450), color = "blue")

# calculate REG utilisation by period
dispatchload_orig %>% 
  filter(RAISEREG > 0 & LOWERREG == 0) %>% 
  mutate(REG_UTIL_MW = case_when(DUID == "VBBG1" ~ INITIALMW - TOTALCLEARED,
                                       DUID == "VBBL1" ~ TOTALCLEARED - INITIALMW,
                                       DUID == "VBB1" & TOTALCLEARED >= 0 ~ INITIALMW - TOTALCLEARED,
                                       DUID == "VBB1" & TOTALCLEARED < 0 ~ INITIALMW - TOTALCLEARED)) %>%
  filter(REG_UTIL_MW >= 0) %>% 
  mutate(util_rate = REG_UTIL_MW/RAISEREG) %>% 
  filter(util_rate <= 1 & util_rate >= 0) %>% 
  group_by(period) %>% 
  mutate(mean_util_rate = mean(util_rate)) %>% 
  ungroup() %>% 
  ggplot() +
  geom_boxplot(aes(x = period, y = util_rate, group = period)) +
  geom_point(aes(x = period, y = mean_util_rate))

dispatchload_orig %>% 
  filter(RAISEREG == 0 & LOWERREG > 0) %>% 
  mutate(REG_UTIL_MW = case_when(DUID == "VBBL1" ~ INITIALMW - TOTALCLEARED,
                                       DUID == "VBBG1" ~ TOTALCLEARED - INITIALMW,
                                       DUID == "VBB1" & TOTALCLEARED >= 0 ~ TOTALCLEARED - INITIALMW,
                                       DUID == "VBB1" & TOTALCLEARED < 0 ~ INITIALMW - TOTALCLEARED)) %>%
  filter(REG_UTIL_MW >= 0) %>% 
  mutate(util_rate = REG_UTIL_MW/LOWERREG) %>% 
  filter(util_rate <= 1 & util_rate >= 0) %>% 
  group_by(period) %>% 
  mutate(mean_util_rate = mean(util_rate)) %>% 
  ungroup() %>% 
  ggplot() +
  geom_boxplot(aes(x = period, y = util_rate, group = period)) +
  geom_point(aes(x = period, y = mean_util_rate))

# outages - days without any wholesale energy traded
dispatchload_orig %>% 
  mutate(TOTALCLEARED = case_when(DUID == "VBBL1" ~ -1*TOTALCLEARED,
                                  TRUE ~ TOTALCLEARED)) %>% 
  group_by(SETTLEMENTDATE) %>% 
  mutate(LARGEST_VOL = max(abs(TOTALCLEARED))) %>% 
  ungroup() %>% 
  filter(abs(TOTALCLEARED) == LARGEST_VOL) %>%
  filter(TOTALCLEARED != 0) %>% 
  distinct(SETTLEMENTDATE) %>% 
  mutate(time_diff = time_length(SETTLEMENTDATE - lag(SETTLEMENTDATE, n = 1), unit = "days")) %>% 
  filter(time_diff >= 1)

# rolling SOC based on cleared volumes
dispatchload_orig %>% 
  mutate(TOTALCLEARED = case_when(DUID == "VBBL1" ~ -1*TOTALCLEARED*sqrt(0.85),
                                  TRUE ~ TOTALCLEARED/sqrt(0.85))) %>% 
  group_by(SETTLEMENTDATE, period) %>% 
  summarise(TOTALCLEARED = sum(TOTALCLEARED),
            raisereg = sum(RAISEREG),
            lowerreg = sum(LOWERREG)) %>% 
  ungroup() %>% 
  mutate(TOTALCLEARED = 0.5*(TOTALCLEARED + lag(TOTALCLEARED, n = 1, default = 0)),
         energy_delta = (lowerreg * 0.09 - raisereg * 0.21 - TOTALCLEARED)/12) %>% 
  group_by(period) %>% 
  mutate(soc = cumsum(energy_delta)) %>% 
  ungroup() %>% 
  filter(period == "P1" & SETTLEMENTDATE >= "2021-12-08 04:00:00") %>% 
  ggplot() +
  geom_line(aes(x = SETTLEMENTDATE, y = soc))

  
# unique constraints with VBB trader term
constraints <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/genericconstraintrhs_SPDID_VBB_T.csv") %>% 
  distinct(GENCONID, SCOPE)

constraints1 <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchconstraint_20211208.csv")
constraints2 <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchconstraint_20220315.csv")
constraints3 <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchconstraint_20230427.csv")
constraints4 <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchconstraint_20240318.csv")
constraints5 <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchconstraint_20250216.csv")

constraint_superset <- constraints1 %>% 
  rbind(constraints2) %>% 
  rbind(constraints3) %>% 
  rbind(constraints4) %>% 
  rbind(constraints5) %>% 
  distinct()
  
vbb_local_price <- constraint_superset %>% 
  filter(CONSTRAINTID %in% filter(constraints, SCOPE == "DS")$GENCONID) %>% 
  filter(MARGINALVALUE != 0)
  