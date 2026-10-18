# Electricity consumption, price and bill dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://electricity-dashboard-8xb7paadydr96th2e8o3v5.streamlit.app/)

Streamlit app that joins hourly electricity consumption and temperature data with hourly spot
prices, calculates the hourly bill and visualises consumption, bill, average price and average
temperature over a selected period, grouped daily, weekly or monthly.

**Live app:** https://electricity-dashboard-8xb7paadydr96th2e8o3v5.streamlit.app/
(hosted on Streamlit Community Cloud, redeploys automatically on every push to `main`)

## Files

| File | Content |
| --- | --- |
| `electricity_app.py` | Streamlit application |
| `Electricity_consumption_2015-2025.csv` | Hourly consumption (kWh) and temperature (°C) — comma separated |
| `Electricity_price_2015-2025.csv` | Hourly price (cents/kWh) — semicolon separated, decimal comma, `HH:MM MM/DD/YYYY` time stamps |
| `requirements.txt` | Python packages |

## Run

```bash
pip install -r requirements.txt
streamlit run electricity_app.py
```

Directly from GitHub:

```bash
streamlit run https://raw.githubusercontent.com/Walid-Barakat/electricity-dashboard/main/electricity_app.py
```

Publishing and submission steps: see [SUBMISSION.md](SUBMISSION.md).

## What the app does

1. Converts the time columns of both files to pandas datetime.
2. Joins the two data frames on time (the repeated hour at the autumn daylight-saving change is
   matched by order of occurrence).
3. Calculates the hourly bill: `Bill [€] = kWh × Price [cents/kWh] / 100`.
4. Groups the data daily, weekly or monthly: consumption and bill are summed, price and
   temperature are averaged.
5. Visualises it with a date-range selector, key figures for the period, a grouping selector and
   line graphs.

Extra insights: average hourly profile of consumption and price, temperature vs. consumption
correlation, comparison with a fixed price contract, most expensive hours and negative-price hours.
