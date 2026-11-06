# %%
# %pip install pandas 

import pandas as pd
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
data_dir = project_dir / "fred_data"

# %%
cpi = pd.read_csv(data_dir / "cpi.csv")
cpi.head()

ffr = pd.read_csv(data_dir / "federal_funds_rate.csv")
ffr.head()

m2 = pd.read_csv(data_dir / "m2_money_supply.csv")
m2.head()

oil_price = pd.read_csv(data_dir / "oil_prices_wti.csv")
oil_price.head()

rgdp = pd.read_csv(data_dir / "real_gdp.csv")
rgdp.head()

unemployment = pd.read_csv(data_dir / "unemployment_rate.csv")
unemployment.head()

# %%
dataframes = [cpi, ffr, m2, oil_price, rgdp, unemployment]

for dfs in dataframes:
    print(dfs.head())

# %%
cpi["date"] = pd.to_datetime(cpi["date"]).dt.strftime("%Y-%m")

ffr["date"] = pd.to_datetime(ffr["date"]).dt.strftime("%Y-%m")

m2["date"] = pd.to_datetime(m2["date"]).dt.strftime("%Y-%m")

oil_price["date"] = pd.to_datetime(oil_price["date"]).dt.strftime("%Y-%m")

rgdp["date"] = pd.to_datetime(rgdp["date"]).dt.strftime("%Y-%m")

unemployment["date"] = pd.to_datetime(unemployment["date"]).dt.strftime("%Y-%m")

# %%
for df in dataframes:
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("Q")

# %%
dataframes = [cpi, ffr, m2, oil_price, unemployment]

for i, df in enumerate(dataframes):
    dataframes[i] = (
        df.groupby("date", as_index=False)
        .agg(value=("value", "mean"))
    )

cpi, ffr, m2, oil_price, unemployment = dataframes

# %%
cpi["cpi_value"] = cpi["value"]
ffr["ffr_value"] = ffr["value"]
m2["m2_value"] = m2["value"]
oil_price["oil_price_value"] = oil_price["value"]
rgdp["rgdp_value"] = rgdp["value"]
unemployment["unemployment_value"] = unemployment["value"]

# %%
dataframe = cpi.merge(
    ffr[["date", "ffr_value"]],
    on = "date",
    how = "right"
)

dataframe = dataframe.merge(
    m2[["date", "m2_value"]],
        on = "date",
        how = "right"
)

dataframe = dataframe.merge(
    oil_price[["date", "oil_price_value"]],
        on = "date",
        how = "right"
)

dataframe = dataframe.merge(
    rgdp[["date", "rgdp_value"]],
        on = "date",
        how = "right"
)

dataframe = dataframe.merge(
    unemployment[["date", "unemployment_value"]],
        on = "date",
        how = "right"
)

dataframe = dataframe.drop(columns = ["value"])
dataframe = dataframe.dropna()
dataframe = dataframe.sort_values("date").reset_index(drop=True)

print(dataframe["date"].isna().sum())
print(dataframe["date"].duplicated().sum())

assert dataframe["date"].notna().all(), "Missing dates found"
assert dataframe["date"].is_unique, "Duplicated dates are found"

dataframe.head()

dataframe.to_csv(data_dir / "final_dataset.csv", index = False)

# %%
dataframe["lag1_cpi_value"] = dataframe["cpi_value"].shift(1)
dataframe["lag1_ffr_value"] = dataframe["ffr_value"].shift(1)
dataframe["lag1_m2_value"] = dataframe["m2_value"].shift(1)
dataframe["lag1_oil_price_value"] = dataframe["oil_price_value"].shift(1)
dataframe["lag1_rgdp_value"] = dataframe["rgdp_value"].shift(1)
dataframe["lag1_unemployment_value"] = dataframe["unemployment_value"].shift(1)

# %%
dataframe["lag2_cpi_value"] = dataframe["cpi_value"].shift(2)
dataframe["lag2_ffr_value"] = dataframe["ffr_value"].shift(2)
dataframe["lag2_m2_value"] = dataframe["m2_value"].shift(2)
dataframe["lag2_oil_price_value"] = dataframe["oil_price_value"].shift(2)
dataframe["lag2_rgdp_value"] = dataframe["rgdp_value"].shift(2)
dataframe["lag2_unemployment_value"] = dataframe["unemployment_value"].shift(2)

# %%
dataframe["lag3_cpi_value"] = dataframe["cpi_value"].shift(3)
dataframe["lag3_ffr_value"] = dataframe["ffr_value"].shift(3)
dataframe["lag3_m2_value"] = dataframe["m2_value"].shift(3)
dataframe["lag3_oil_price_value"] = dataframe["oil_price_value"].shift(3)
dataframe["lag3_rgdp_value"] = dataframe["rgdp_value"].shift(3)
dataframe["lag3_unemployment_value"] = dataframe["unemployment_value"].shift(3)

# %%
dataframe["lag4_cpi_value"] = dataframe["cpi_value"].shift(4)
dataframe["lag4_ffr_value"] = dataframe["ffr_value"].shift(4)
dataframe["lag4_m2_value"] = dataframe["m2_value"].shift(4)
dataframe["lag4_oil_price_value"] = dataframe["oil_price_value"].shift(4)
dataframe["lag4_rgdp_value"] = dataframe["rgdp_value"].shift(4)
dataframe["lag4_unemployment_value"] = dataframe["unemployment_value"].shift(4)

# %%
dataframe["time_trend"] = range(0, len(dataframe))

# %%
# 날짜 중복 확인
print(dataframe["date"].isna().sum())
print(dataframe["date"].duplicated().sum())

assert dataframe["date"].notna().all(), "Missing dates found"
assert dataframe["date"].is_unique, "Duplicated dates are found"

# 분기별 연속성 확인
expected_dates = pd.period_range(
    start = dataframe["date"].min(),
    end=  dataframe["date"].max(),
    freq="Q"
)

missing_dates = expected_dates.difference(dataframe["date"])

print("Missing quarters:", missing_dates)

# %%
print(dataframe.head(10))

# %%
dataframe.to_csv(data_dir / "final_dataset_lagged.csv", index = False)


