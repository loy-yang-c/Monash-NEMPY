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
  filter(BIDTYPE == "LOWER5MIN") %>% 
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
  filter(SETTLEMENTDATE >= "2024-04-01") %>% 
  filter(BIDTYPE == "ENERGY" & DIRECTION == "GEN") %>% 
  ggplot() +
  geom_boxplot(aes(x = PERIODID, y = MAXAVAIL, group = PERIODID))

capacitybands_nonsips %>% 
  filter(SETTLEMENTDATE >= "2021-12-08") %>% 
  filter(BIDTYPE == "RAISEREG" & DIRECTION == "LOAD") %>% 
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
dispatchload <- read_csv("C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchload.csv")

dispatchload <- dispatchload %>% 
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
                            month(SETTLEMENTDATE) < 11 & yr == 2026 ~ "P5b"),
         BIDTYPE = case_when(DUID == "VBBG1" ~ "GEN",
                             DUID == "VBBL1" ~ "LOAD",
                             DUID == "VBB1" & TOTALCLEARED >= 0 ~ "GEN",
                             DUID == "VBB1" & TOTALCLEARED < 0 ~ "LOAD"))

temp <- dispatchload %>% 
  select(-BIDTYPE, -TOTALCLEARED) %>% 
  pivot_longer(cols = c("LOWER5MIN", "LOWER60SEC", "LOWER6SEC","LOWER1SEC",
                        "RAISE5MIN", "RAISE60SEC", "RAISE6SEC", "RAISE1SEC",
                        "RAISEREG", "LOWERREG"), names_to = "BIDTYPE", values_to = "TOTALCLEARED")

dispatchload <- dispatchload %>% 
  select(-c("LOWER5MIN", "LOWER60SEC", "LOWER6SEC", "LOWER1SEC",
            "RAISE5MIN", "RAISE60SEC", "RAISE6SEC", "RAISE1SEC",
            "RAISEREG", "LOWERREG")) %>% 
  rbind(temp) %>% 
  arrange(SETTLEMENTDATE)  %>% 
  mutate(TOTALCLEARED = abs(TOTALCLEARED))

dispatchload %>% 
  filter(BIDTYPE == "LOWER1SEC") %>% 
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
  
  