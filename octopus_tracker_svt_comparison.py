import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Tariffs
TRACKER = "SILVER-23-12-06"
SVT = "VAR-22-11-01"
REGION = "C"

# URLS
URL_BASE = "https://api.octopus.energy/v1/products"
URL_TRACKER = f"{URL_BASE}/{TRACKER}/electricity-tariffs/E-1R-{TRACKER}-{REGION}"
URL_SVT = f"{URL_BASE}/{SVT}/electricity-tariffs/E-1R-{SVT}-{REGION}"

TIMEOUT = 5


# Tracker unit rates
dict_tracker_unit = requests.get(
    f"{URL_TRACKER}/standard-unit-rates/?page_size=1500",
    timeout=TIMEOUT).json()

df_tracker_unit = pd.DataFrame(
    data = [
        day['value_inc_vat'] for day in dict_tracker_unit['results']
            if day['payment_method'] != "NON_DIRECT_DEBIT"],
    index = pd.to_datetime(
        [day['valid_from'] for day in dict_tracker_unit['results']
             if day['payment_method'] != "NON_DIRECT_DEBIT"]),
    columns = [f"{TRACKER}-{REGION}"])


# SVT unit rates
dict_svt_unit = requests.get(
    f"{URL_SVT}/standard-unit-rates/?page_size=1500",
    timeout=TIMEOUT).json()

df_svt_unit = pd.DataFrame(
    data = [
        day['value_inc_vat'] for day in dict_svt_unit['results']
            if day['payment_method'] != "NON_DIRECT_DEBIT"],
    index = pd.to_datetime(
        [day['valid_from'] for day in dict_svt_unit['results']
             if day['payment_method'] != "NON_DIRECT_DEBIT"]),
    columns = [f"{SVT}-{REGION}"])


# Merge tracker and SVT info
df_prices = df_tracker_unit.join(df_svt_unit, how="outer")
df_prices[f"{SVT}-{REGION}"] = df_prices[f"{SVT}-{REGION}"].ffill()

# Restrict data to just tracker tariff period
df_prices = df_prices.dropna(subset=f"{TRACKER}-{REGION}")


# Export data as CSV
df_prices.sort_index(inplace=True, ascending=False)
df_prices.to_csv('octo_tracker_vs_svt.csv')


# Generate plot
sns.set_theme()
sns.set_context("paper")
plt.figure(figsize=(12, 7.5), dpi=300)
plt_price = sns.lineplot(df_prices, markers={f"{TRACKER}-{REGION}": "o", f"{SVT}-{REGION}": ","})
plt_price.set(xlabel='Date', ylabel="Unit rate (pence)")
plt_price.set_ylim(0,)
sns.move_legend(plt_price, "lower right")
fig = plt_price.get_figure()
fig.savefig("octo_tracker_vs_svt.png", bbox_inches='tight')
