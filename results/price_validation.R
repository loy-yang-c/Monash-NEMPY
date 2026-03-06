library(tidyverse); library(plotly)

nempy_energy <- read_csv("nem_full_energy_2021-11-29_2022-01-01.csv")
nempy_fcas <- read_csv("nem_full_fcas_2021-11-29_2022-01-01.csv")
nempy_local <- read_csv("nem_full_local_2021-11-29_2022-01-01.csv")

dispatchprice <- read_csv("research/nemweb/dispatchprice.csv")
dispatchconstraint <- read_csv("dispatchconstraint_20220315.csv")

# check RRN price accuracy
data_energy <- nempy_energy %>% 
  mutate(interval = ymd_hms(interval)) %>% 
  select(interval, region, price_run1, price_run2, price) %>% 
  left_join(dispatchprice, by = c("interval"="SETTLEMENTDATE", "region"="REGIONID"))

# summary of within 5c differences
data_energy %>% 
  group_by(interval) %>% 
  mutate(dispatch_run = case_when(sum(price_run1) == sum(price) ~ "r1",
                                  sum(price_run1) == sum(price_run2) ~ "same",
                                  TRUE ~ "r2")) %>% 
  ungroup() %>% 
  mutate(accurate = case_when(abs(price - ROP) < 0.05 ~ 1,
                              TRUE ~ 0),
         alt_price = case_when(dispatch_run == "r1" ~ price_run2,
                               TRUE ~ price_run1),
         alt_accurate = case_when(abs(alt_price - ROP) < 0.05 ~ 1,
                                  TRUE ~ 0)) %>% 
  group_by(dispatch_run, region, INTERVENTION, OCD_STATUS) %>% 
  summarise(intervals = n(),
            accurate = sum(accurate),
            perc = accurate/intervals,
            alt_accurate = sum(alt_accurate),
            alt_perc = alt_accurate/intervals) %>% 
  ungroup() %>% 
  arrange(desc(intervals)) %>% 
  View()

# boxplot of price errors
p <- data_energy %>% 
  mutate(error = price - ROP) %>% 
  ggplot() +
  geom_boxplot(aes(x = region, y = error)) +
  theme_minimal()

ggplotly(p)

# comparison of constraint marginal values
data_constraints <- nempy_local %>% 
  mutate(interval = ymd_hms(interval)) %>% 
  select(interval, set, price_run1, price_run2, price) %>% 
  left_join(dispatchconstraint, by = c("interval" = "SETTLEMENTDATE", "set"="CONSTRAINTID"))

# boxplot of constraint marginal value errors
p <- data_constraints %>% 
  mutate(error = price - MARGINALVALUE) %>% 
  group_by(set) %>% 
  mutate(agg_error = sum(abs(error))) %>% 
  ungroup() %>% 
  filter(agg_error > 0) %>% 
  ggplot() +
  geom_boxplot(aes(x = reorder(set, -error, FUN = median), y = error)) +
  coord_flip() +
  theme_minimal()

ggplotly(p)  

# check for constraint prices that are ever non-zero
data_constraints %>% 
  group_by(set) %>% 
  summarise(n = sum(price != 0),
         ave = mean(price)) %>% 
  ungroup() %>% 
  filter(n > 0) %>% 
  View()

# inspect price elasticity runs
central_price <- read_csv("results/nem_full - parallel_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_up1 <- read_csv("results/nem_full - parallel - +50 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_up2 <- read_csv("results/nem_full - parallel - +100 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_up3 <- read_csv("results/nem_full - parallel - +150 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_up4 <- read_csv("results/nem_full - parallel - +200 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_up5 <- read_csv("results/nem_full - parallel - +250 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_down3 <- read_csv("results/nem_full - parallel - -150 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_down4 <- read_csv("results/nem_full - parallel - -200 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)
elasticity_down5 <- read_csv("results/nem_full - parallel - -250 VIC1_energy_2021-11-29_2022-01-01.csv") %>% 
  filter(region == "VIC1") %>% 
  select(interval, price) %>% 
  rename("energy_price" = price)

data <- central_price %>% 
  select(interval, energy_price) %>% 
  left_join(
    rename(elasticity_up1, "+demand_1" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_up2, "+demand_2" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_up3, "+demand_3" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_up4, "+demand_4" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_up5, "+demand_5" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_down3, "-demand_3" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_down4, "-demand_4" = energy_price),
    by = "interval") %>% 
  left_join(
    rename(elasticity_down5, "-demand_5" = energy_price),,
    by = "interval")

p <- data %>% 
  pivot_longer(cols = energy_price:`-demand_5`, names_to = "series", values_to = "price") %>% 
  mutate(interval = ymd_hms(interval)) %>% 
  ggplot() +
  geom_line(aes(x = interval, y = price, color = series)) +
  theme_minimal()

ggplotly(p)

# check that all changes to demand are weakly monotonic
# -- weird things happen sometimes, a lower ROP in VIC from lower total system cost can arise
data %>% 
  mutate(monotonic = case_when((`-demand_5` <= `-demand_4` + 0.00001) &
                               (`-demand_4` <= `-demand_3` + 0.00001) &
                               (`-demand_3` <= energy_price + 0.00001) &
                               (energy_price <= `+demand_1` + 0.00001) &
                               (`+demand_1` <= `+demand_2` + 0.00001) & 
                               (`+demand_2` <= `+demand_3` + 0.00001) &
                               (`+demand_3` <= `+demand_4` + 0.00001) &
                               (`+demand_4` <= `+demand_5` + 0.00001) ~ 1,
                               TRUE ~ 0)) %>% 
  filter(monotonic != 1)

# let's view segment price increase
data %>% 
  filter(interval %in% sample(unique(data$interval), size = 250, replace = FALSE)) %>% 
  mutate(across(`+demand_1`:`-demand_5`, ~ .x - energy_price)) %>% 
  select(-energy_price) %>% 
  pivot_longer(cols = `+demand_1`:`-demand_5`, names_to = "segment_name", values_to = "delta_price") %>% 
  mutate(segment = as.integer(paste0(substr(segment_name, 1, 1), substr(segment_name, 9, 9)))) %>% 
  ggplot() +
  #geom_point(aes(x = delta_price, y = segment), alpha = 0.1) +
  geom_line(aes(x = delta_price, y = segment, group = interval), alpha = 0.25) +
  theme_minimal() +
  #xlim(-250, 250) +
  scale_y_continuous(breaks = seq(-5, 5, by = 1))

data %>% 
  mutate(across(`+demand_1`:`-demand_5`, ~ .x - energy_price)) %>% 
  select(-energy_price) %>% 
  pivot_longer(cols = `+demand_1`:`-demand_5`, names_to = "segment_name", values_to = "delta_price") %>% 
  mutate(segment = as.integer(paste0(substr(segment_name, 1, 1), substr(segment_name, 9, 9)))) %>% 
  ggplot() +
  geom_boxplot(aes(x = delta_price, y = segment, group = segment), alpha = 0.25) +
  theme_minimal() +
  xlim(-250, 250) +
  scale_y_continuous(breaks = seq(-5, 5, by = 1))

data %>% 
  mutate(across(`+demand_1`:`-demand_5`, ~ .x - energy_price)) %>% 
  pivot_longer(cols = `+demand_1`:`-demand_5`, names_to = "segment_name", values_to = "delta_price") %>% 
  mutate(segment = as.integer(paste0(substr(segment_name, 1, 1), substr(segment_name, 9, 9)))) %>% 
  filter(segment %in% c(-5, 5)) %>% 
  ggplot() +
  geom_point(aes(x = energy_price, y = delta_price), alpha = 0.5) +
  theme_minimal() +
  facet_wrap(~segment_name, scales = "free", nrow = 2)



