library(tidyverse); library(plotly)

nempy_energy <- read_csv("nem_full_energy_2021-11-29_2022-01-01.csv")
nempy_fcas <- read_csv("nem_full_fcas_2021-11-29_2022-01-01.csv")
nempy_local <- read_csv("nem_full_local_2021-11-29_2022-01-01.csv")

dispatchprice <- read_csv("dispatchprice.csv")
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

# for many constraints, Basslink in particular, constraint prices are very far off
# check for RHS differences