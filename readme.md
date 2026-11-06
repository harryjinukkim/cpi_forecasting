# Forecasting Quarterly CPI Changes with AR and VAR Models

## Project Overview

This project evaluates the forecasting performance of autoregressive (AR) and vector autoregressive (VAR) models for quarterly changes in the U.S. Consumer Price Index (CPI). I intended to test whether a CPI prediction model from the pre-COVID period would remain valid during the pandemic. Therefore, both AR and VAR models were built based on data from before the COVID pandemic.

The analysis uses six macroeconomic indicators: CPI, the federal funds rate, M2 money supply, WTI crude oil prices, real GDP, and the unemployment rate. Daily and monthly observations are aggregated into quarterly averages, while real GDP is retained at its original quarterly frequency. The series are first-differenced to address nonstationarity.

Two AR models were used, one with 2 lags and another with 4 lags. A VAR model with 2 lags was used, since this was considered the best lag order according to the lag selection procedure. I evaluated the forecasting performance of the models by comparing their RMSE and MAE values obtained from out-of-sample testing.

## Forecasting Approach

The AR models use past changes in CPI, while the VAR model includes changes in all six indicators. The VAR lag order is selected using the Bayesian Information Criterion (BIC).

The models are estimated using observations before 2020Q1. Their coefficients remain fixed during evaluation, while the observed data used to generate forecasts are updated at each forecast origin.

Two forecast horizons are evaluated:

- **Horizon 1:** One-quarter-ahead forecasts, evaluated over 2020Q1–2023Q1.
- **Horizon 2:** Two-quarter-ahead forecasts, evaluated over 2020Q2–2023Q1.

For two-quarter-ahead forecasts, the predicted value for the first quarter is used to generate the next prediction. The forecast target is the change in the CPI index, measured in index points, rather than the percentage inflation rate.

## Results

Lower RMSE and MAE values indicate smaller forecast errors.

| Model | Forecast horizon | RMSE | MAE |
|---|---|---|---|
| VAR(2) | 1 quarter | 3.54201447446453 | 3.096952458843927 |
| VAR(2) | 2 quarters | 3.468206809379034 | 3.0684884322292643 |
| AR(4) | 1 quarter | 3.151855629058562 | 2.776587410966341 |
| AR(4) | 2 quarters | 3.844923768710656 | 3.451395104931892 |
| AR(2) | 1 quarter | 3.0493131528855963 | 2.6652461067244606 |
| AR(2) | 2 quarters | 3.6998943256510817 | 3.308324800414473 |

In the end, the most accurate model was the AR(2) model with a horizon of 1 quarter, while the second most accurate model was AR(4) with a horizon of 1 quarter.

These two specifications have the lowest errors among the reported results. However, model comparisons should also be made within each forecast horizon, since the horizons represent different forecasting tasks and have slightly different evaluation periods. AR(2) performs best at the one-quarter horizon, while VAR(2) performs best at the two-quarter horizon.

Both model notebooks include graphs comparing actual CPI changes with forecasts from AR(2), AR(4), and VAR. These graphs help identify periods when the models overpredict or underpredict CPI changes.

## Repository Structure

```text
Macro_Update/
├── fred_data/
│   ├── ... individual FRED series
│   ├── final_dataset.csv
│   └── final_dataset_lagged.csv
├── jupyter/
│   ├── macro_data_merge.ipynb
│   ├── AR_Model.ipynb
│   └── VAR_Model.ipynb
├── python/
│   ├── data_update_manual.py
│   ├── data_update_automatic.py
│   ├── data_merge.py
│   └── news_collect.py
└── .gitignore
```

## How to Run

Run the following commands from the project root.

### 1. Install dependencies

```bash
python3 -m pip install pandas numpy scipy statsmodels scikit-learn matplotlib jupyterlab
```

### 2. Run the analysis

The repository includes the prepared CSV files, so API keys are not required to run the model notebooks.

```bash
python3 -m jupyterlab
```

Open `jupyter/AR_Model.ipynb` or `jupyter/VAR_Model.ipynb` and run all cells from the top. Each notebook generates the model comparison graph independently.

### 3. Refresh the data — optional

Create a local `python/.env` file containing:

```dotenv
FRED_API_KEY=your_fred_api_key
```

Download updated FRED observations:

```bash
python3 python/data_update_manual.py
```

Then rebuild the merged datasets using `python/data_merge.py` or `jupyter/macro_data_merge.ipynb`. The Python script locates `fred_data` relative to its own file. Run the preprocessing notebook with its working directory set to the project root or the `jupyter` folder.

Rerun the model notebooks after rebuilding the datasets. Updated or revised FRED observations may change the reported results.

## Optional News Collection

The project also includes a separate news collection script covering U.S.–Iran conflict developments, U.S. unemployment, and index funds. It uses OpenAI web search to produce Korean summaries with source links.

```bash
python3 -m pip install --upgrade openai
```

Add `OPENAI_API_KEY` to the local `python/.env` file, then run:

```bash
python3 python/news_collect.py
```

By default, the script requests up to five items per topic from the past seven days and saves Markdown and JSON files under `news_data/`. API usage may incur charges. This feature is separate from the forecasting models; news is not used as a model input.

API keys must remain local and must not be committed to GitHub.

## Limitations

- The models use fixed pre-pandemic coefficients, which may not capture changes in economic relationships during the pandemic.
- The analysis uses downloaded historical data rather than the exact data releases available at each forecast origin. It therefore does not replicate real-time forecasting conditions.
- The evaluation period is short, and the results may not generalize to other periods.
- The comparison does not include a simple benchmark, such as a historical-mean forecast. It measures relative performance among the selected AR and VAR specifications.
- First differencing addresses nonstationarity but does not guarantee that all model assumptions hold.

## Data Source

The macroeconomic series are obtained from Federal Reserve Economic Data (FRED), maintained by the Federal Reserve Bank of St. Louis:

`CPIAUCSL`, `FEDFUNDS`, `M2SL`, `DCOILWTICO`, `GDPC1`, and `UNRATE`.