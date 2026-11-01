# Stock Portfolio Performance Tracker

A Python 3 console application for tracking stock holdings and calculating portfolio performance.

## Project files

- `portfolio.py` — main interactive portfolio tracker.
- `sp500_tickers.csv` — the S&P 500 ticker/company dataset supplied with the task (503 rows in the supplied file).
- `portfolio_summary.csv` — generated automatically when you run the program.
- `requirements.txt` — optional dependency for live price lookups.
- `README.md` — instructions.

## Features

- Validates ticker symbols against the supplied S&P 500 dataset.
- Accepts ticker, number of shares, and purchase price.
- Combines repeated purchases of the same stock and calculates weighted average purchase price.
- Tries to retrieve a current quote using optional `yfinance`.
- If live quote retrieval is unavailable, asks the user to enter the current price manually.
- Calculates invested capital, current market value, gain/loss, and gain/loss percentage for each holding.
- Calculates total portfolio value and overall return.
- Appends holding-level and total performance records to `portfolio_summary.csv` with a timestamp.

## Important note about the supplied dataset

The provided CSV contains company symbols and company information. It does **not** contain stock prices. Therefore, the program uses optional `yfinance` for quote lookup; if that is unavailable, you enter the current price yourself. Manual prices are clearly labelled in the report and CSV log. Live quotes can be delayed, unavailable, or subject to provider limitations.

## Requirements

- Python 3.8 or later.
- No required third-party package for manual-price mode.
- Optional live price support: `yfinance`.

## Run the project

Open a terminal in this folder:

```bash
python portfolio.py
```

To use manual prices only:

```bash
python portfolio.py --manual-prices
```

To install optional live quote support:

```bash
pip install -r requirements.txt
```

Then run `python portfolio.py` again.

## Example workflow

1. Enter `AAPL`.
2. Enter the number of shares, such as `5`.
3. Enter the purchase price per share, such as `180`.
4. Add more holdings, or type `DONE`.
5. The program attempts a live quote. If it cannot get one, enter the current price manually.
6. Review the portfolio report.
7. Open `portfolio_summary.csv` to see the saved history.

The sample numbers above are only an illustration; they are not current market prices.

## Formulas

- Invested value = shares × purchase price.
- Average purchase price = total invested value ÷ total shares.
- Current market value = shares × current price.
- Gain/loss = current market value − invested value.
- Gain/loss % = (gain/loss ÷ invested value) × 100.
- Portfolio return % = (total market value − total invested) ÷ total invested × 100.

## CSV logging

Each run appends one `HOLDING` row for each stock and one `PORTFOLIO_TOTAL` row. The log is not overwritten, so previous snapshots remain available.
