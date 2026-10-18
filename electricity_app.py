"""
Electricity consumption, price and bill dashboard (Streamlit).

Run locally:
    streamlit run electricity_app.py

Run directly from GitHub (after uploading this script + both CSV files):
    streamlit run https://raw.githubusercontent.com/Walid-Barakat/electricity-dashboard/main/electricity_app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Data location
# ---------------------------------------------------------------------------
# When the script is started from a raw.githubusercontent link, Streamlit
# downloads only the script, so the CSV files are read from GitHub as well.
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Walid-Barakat/electricity-dashboard/main/"

CONSUMPTION_FILE = "Electricity_consumption_2015-2025.csv"
PRICE_FILE = "Electricity_price_2015-2025.csv"


def data_source(file_name: str) -> str:
    """Use the local file if it sits next to the script, otherwise GitHub."""
    local = Path(__file__).parent / file_name
    return str(local) if local.exists() else GITHUB_RAW_BASE + file_name


# ---------------------------------------------------------------------------
# Data preparation (tasks 1-3)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    # Consumption file: comma separated, ISO time stamps "2015-01-01 00:00:00"
    consumption = pd.read_csv(data_source(CONSUMPTION_FILE))

    # Price file: semicolon separated, decimal comma ("3,47"),
    # time stamps in the format "00:00 01/01/2015" (hour:minute month/day/year)
    price = pd.read_csv(data_source(PRICE_FILE), sep=";", decimal=",")

    # 1) Change the time format of both files to pandas datetime
    consumption["time"] = pd.to_datetime(consumption["time"], format="%Y-%m-%d %H:%M:%S")
    price["time"] = pd.to_datetime(price.pop("timestamp"), format="%H:%M %m/%d/%Y")

    # The autumn daylight-saving change repeats one hour (e.g. 03:00 twice) in
    # both files. Number repeated time stamps so that the first 03:00 is
    # matched with the first 03:00, the second with the second, etc.
    consumption["n"] = consumption.groupby("time").cumcount()
    price["n"] = price.groupby("time").cumcount()

    # 2) Join the two data frames according to time
    df = pd.merge(consumption, price, on=["time", "n"], how="inner").drop(columns="n")

    # 3) Hourly bill in euros: kWh * (cents/kWh) / 100
    df["Bill"] = df["kWh"] * df["Price"] / 100

    return df.sort_values("time").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Grouping (task 4)
# ---------------------------------------------------------------------------
GROUPING_RULES = {"Daily": "D", "Weekly": "W-MON", "Monthly": "MS"}


def group_data(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Daily / weekly / monthly consumption & bill (sums) and price & temperature (means)."""
    g = df.set_index("time").resample(GROUPING_RULES[interval], label="left", closed="left")
    return pd.DataFrame(
        {
            # min_count=1 keeps periods without any data as gaps instead of 0
            "Consumption": g["kWh"].sum(min_count=1),
            "Bill": g["Bill"].sum(min_count=1),
            "Average price": g["Price"].mean(),
            "Average temperature": g["Temperature"].mean(),
        }
    )


# Y-axis labels for the line graphs
AXIS_LABELS = {
    "Consumption": "Electricity consumption [kWh]",
    "Bill": "Electricity bill [€]",
    "Average price": "Electricity price [cents/kWh]",
    "Average temperature": "Temperature [°C]",
}


# ---------------------------------------------------------------------------
# User interface (task 5)
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Electricity dashboard", page_icon="⚡", layout="centered")
st.title("⚡ Electricity consumption, price and bill")
st.caption(
    "Hourly consumption and outdoor temperature joined with hourly spot prices "
    "(cents/kWh). Bill = consumption × price."
)

data = load_data()
first_day = data["time"].min().date()
last_day = data["time"].max().date()

# --- Selector for the time interval included in the analysis -------------
col_start, col_end = st.columns(2)
start_date = col_start.date_input(
    "Start time", value=pd.Timestamp("2022-01-01").date(),
    min_value=first_day, max_value=last_day, format="YYYY/MM/DD",
)
end_date = col_end.date_input(
    "End time", value=pd.Timestamp("2024-06-01").date(),
    min_value=first_day, max_value=last_day, format="YYYY/MM/DD",
)

if start_date > end_date:
    st.error("Start time must be before end time.")
    st.stop()

start = pd.to_datetime(start_date)
end = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # include the whole end day
selected = data[(data["time"] >= start) & (data["time"] < end)]

if selected[["kWh", "Price"]].dropna().empty:
    st.warning("No consumption/price data in the selected range.")
    st.stop()

# --- Key figures over the selected period ---------------------------------
total_kwh = selected["kWh"].sum()
total_bill = selected["Bill"].sum()
avg_price = selected["Price"].mean()
# Average price actually paid = bill / consumption (consumption-weighted price),
# using only hours where both consumption and price are known
billed = selected.dropna(subset=["Bill"])
paid_price = 100 * billed["Bill"].sum() / billed["kWh"].sum()
avg_temp = selected["Temperature"].mean()

st.write(f"Showing range: `{start_date}` - `{end_date}`")
st.write("Total consumption over the period:", f"`{total_kwh:,.1f}`", "kWh")
st.write("Total bill over the period:", f"`{total_bill:,.1f}`", "€")
st.write("Average hourly price:", f"`{avg_price:.2f}`", "cents")
st.write("Average paid price:", f"`{paid_price:.2f}`", "cents")
st.write("Average temperature:", f"`{avg_temp:.1f}`", "°C")

if paid_price < avg_price:
    st.success(
        f"Your consumption timing beat the market: you paid {avg_price - paid_price:.2f} "
        "cents/kWh less than the average hourly price."
    )
else:
    st.info(
        f"You paid {paid_price - avg_price:.2f} cents/kWh more than the average hourly price "
        "- more of your consumption fell into expensive hours."
    )

# --- Selector for grouping interval + line graphs -------------------------
interval = st.selectbox("Averaging period:", list(GROUPING_RULES), index=1)
grouped = group_data(selected, interval)

for column in grouped.columns:
    fig = px.line(grouped, y=column, labels={"time": "Time", column: AXIS_LABELS[column]})
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------------
# Extra insights
# ---------------------------------------------------------------------------
st.header("Extra insights")

st.subheader("Average day")
st.caption("Average consumption and price for each hour of the day in the selected period.")
by_hour = selected.groupby(selected["time"].dt.hour)[["kWh", "Price"]].mean()
by_hour.index.name = "Hour of day"
c1, c2 = st.columns(2)
for col, field, label in [(c1, "kWh", "Consumption [kWh]"), (c2, "Price", "Price [cents/kWh]")]:
    fig = px.bar(by_hour, y=field, labels={field: label})
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
    col.plotly_chart(fig, width="stretch")

st.subheader("Temperature vs. consumption")
daily = group_data(selected, "Daily").dropna()
corr = daily["Consumption"].corr(daily["Average temperature"])
st.write(
    f"Correlation between daily average temperature and daily consumption: `{corr:.2f}` "
    "(negative = colder days use more electricity, e.g. for heating)."
)
fig = px.scatter(
    daily.reset_index(), x="Average temperature", y="Consumption", color="Average price",
    color_continuous_scale="Viridis", opacity=0.7,
    labels={
        "Average temperature": "Daily average temperature [°C]",
        "Consumption": "Daily consumption [kWh]",
        "Average price": "Price [c/kWh]",
        "time": "Date",
    },
    hover_data=["time"],
)
fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, width="stretch")

st.subheader("Spot price vs. fixed price contract")
fixed_price = st.number_input(
    "Compare with a fixed price contract [cents/kWh]", min_value=0.0, value=10.0, step=0.5
)
fixed_bill = billed["kWh"].sum() * fixed_price / 100
diff = fixed_bill - total_bill
st.write(
    f"With a fixed price of `{fixed_price:.2f}` cents/kWh the bill would have been "
    f"`{fixed_bill:,.1f}` € - the spot price contract was "
    f"**{'cheaper' if diff > 0 else 'more expensive'}** by `{abs(diff):,.1f}` €."
)

st.subheader("Most expensive hours")
top = selected.nlargest(5, "Bill")[["time", "kWh", "Price", "Bill", "Temperature"]]
top = top.round({"kWh": 3, "Price": 2, "Bill": 2, "Temperature": 1})
top.columns = ["Time", "Consumption (kWh)", "Price (cents/kWh)", "Bill (€)", "Temperature (°C)"]
st.dataframe(top, hide_index=True, width="stretch")

negative_hours = (selected["Price"] < 0).sum()
st.write(
    f"Hours with a negative electricity price in the period: `{negative_hours}` "
    f"(you were paid `{-selected.loc[selected['Bill'] < 0, 'Bill'].sum():.2f}` € for using electricity then)."
)

with st.expander("Show grouped data table"):
    st.dataframe(grouped.round(2), width="stretch")
