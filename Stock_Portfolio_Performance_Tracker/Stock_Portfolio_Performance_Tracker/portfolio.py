"""
STOCK PORTFOLIO PERFORMANCE TRACKER
-----------------------------------
Tracks shares, purchase prices, current market values, and gains/losses.

Run:
    python portfolio.py

Optional live prices:
    pip install -r requirements.txt

Without yfinance or an internet connection, the program asks you to enter
the current price manually. The supplied S&P 500 CSV is a ticker/company
directory; it does NOT contain stock prices.
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TICKER_FILE = BASE_DIR / "sp500_tickers.csv"
SUMMARY_FILE = BASE_DIR / "portfolio_summary.csv"

SUMMARY_FIELDS = [
    "timestamp",
    "record_type",
    "symbol",
    "company",
    "shares",
    "buy_price",
    "current_price",
    "invested_value",
    "market_value",
    "gain_loss",
    "gain_loss_pct",
    "price_source",
]


def load_tickers(file_path=TICKER_FILE):
    """Load the supplied S&P 500 symbol/company directory."""
    tickers = {}
    with Path(file_path).open("r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            symbol = row.get("Symbol", "").strip().upper()
            if symbol:
                tickers[symbol] = row.get("Security", symbol).strip()
    if not tickers:
        raise ValueError("The ticker CSV has no valid symbols.")
    return tickers


def read_positive_number(prompt):
    """Read a number greater than zero, rejecting invalid input."""
    while True:
        value = input(prompt).strip().replace(",", "")
        try:
            number = float(value)
            if number <= 0:
                print("Enter a value greater than zero.")
                continue
            return number
        except ValueError:
            print("Invalid number. Example: 12 or 125.50")


def read_symbol(tickers):
    """Read and validate a stock ticker against the supplied directory."""
    while True:
        symbol = input("Enter stock ticker (example: AAPL): ").strip().upper()
        if symbol in tickers:
            return symbol
        print("Ticker not found in the supplied S&P 500 dataset. Try again.")


def get_live_price(symbol):
    """
    Try to obtain a current quote using optional yfinance.
    Returns (price, source); returns (None, message) if unavailable.
    """
    try:
        import yfinance as yf
    except ImportError:
        return None, "yfinance is not installed"

    try:
        ticker = yf.Ticker(symbol)
        fast_info = ticker.fast_info
        price = fast_info.get("lastPrice")
        if price is None:
            history = ticker.history(period="1d", interval="1m")
            if not history.empty:
                price = float(history["Close"].dropna().iloc[-1])
        if price is not None and float(price) > 0:
            return float(price), "yfinance quote"
        return None, "No quote returned"
    except Exception as error:
        return None, f"Live quote unavailable: {error}"


def collect_portfolio(tickers):
    """Collect positions and combine repeated entries using weighted average cost."""
    positions = {}

    print("\nEnter your stock holdings. You can enter the same ticker more than once.")
    print("Type DONE when you have finished adding holdings.\n")

    while True:
        symbol = input("Ticker (or DONE): ").strip().upper()
        if symbol == "DONE":
            break
        if symbol not in tickers:
            print("Ticker not found in the supplied S&P 500 dataset.")
            continue

        shares = read_positive_number("Number of shares: ")
        buy_price = read_positive_number("Purchase price per share: ")

        if symbol not in positions:
            positions[symbol] = {
                "shares": shares,
                "invested": shares * buy_price,
            }
        else:
            positions[symbol]["shares"] += shares
            positions[symbol]["invested"] += shares * buy_price

        print(f"Added {shares:g} share(s) of {symbol}.\n")

    return positions


def calculate_position(symbol, position, company, manual_price=None):
    """Calculate invested value, market value, gain/loss, and percentage."""
    shares = position["shares"]
    invested = position["invested"]
    average_buy_price = invested / shares

    if manual_price is None:
        current_price, source = get_live_price(symbol)
    else:
        current_price, source = manual_price, "manually entered"

    if current_price is None:
        print(f"\n{symbol}: {source}.")
        current_price = read_positive_number(
            f"Enter the current price for {symbol}: "
        )
        source = "manually entered"

    market_value = shares * current_price
    gain_loss = market_value - invested
    gain_loss_pct = (gain_loss / invested) * 100 if invested else 0.0

    return {
        "symbol": symbol,
        "company": company,
        "shares": shares,
        "buy_price": average_buy_price,
        "current_price": current_price,
        "invested_value": invested,
        "market_value": market_value,
        "gain_loss": gain_loss,
        "gain_loss_pct": gain_loss_pct,
        "price_source": source,
    }


def display_report(results):
    """Print a formatted per-stock report and portfolio totals."""
    print("\n" + "=" * 94)
    print("                         STOCK PORTFOLIO PERFORMANCE")
    print("=" * 94)
    print(
        f"{'SYMBOL':<9}{'SHARES':>9}{'BUY PRICE':>13}{'CURRENT':>13}"
        f"{'INVESTED':>14}{'MARKET VALUE':>16}{'GAIN/LOSS':>14}"
    )
    print("-" * 94)

    total_invested = 0.0
    total_market = 0.0

    for item in results:
        total_invested += item["invested_value"]
        total_market += item["market_value"]
        print(
            f"{item['symbol']:<9}{item['shares']:>9.2f}"
            f"{item['buy_price']:>13.2f}{item['current_price']:>13.2f}"
            f"{item['invested_value']:>14.2f}{item['market_value']:>16.2f}"
            f"{item['gain_loss']:>14.2f}"
        )
        print(
            f"         Return: {item['gain_loss_pct']:+.2f}%"
            f" | Price source: {item['price_source']}"
        )

    total_gain = total_market - total_invested
    total_pct = (total_gain / total_invested * 100) if total_invested else 0.0

    print("-" * 94)
    print(f"Total invested capital : {total_invested:,.2f}")
    print(f"Current portfolio value: {total_market:,.2f}")
    print(f"Total gain / loss      : {total_gain:+,.2f} ({total_pct:+.2f}%)")
    print("=" * 94)

    return {
        "invested_value": total_invested,
        "market_value": total_market,
        "gain_loss": total_gain,
        "gain_loss_pct": total_pct,
    }


def save_summary(results, totals, file_path=SUMMARY_FILE):
    """Append holding-level records and one portfolio total row to a CSV log."""
    file_path = Path(file_path)
    file_exists = file_path.exists() and file_path.stat().st_size > 0
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    with file_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDS)
        if not file_exists:
            writer.writeheader()

        for item in results:
            writer.writerow({
                "timestamp": timestamp,
                "record_type": "HOLDING",
                "symbol": item["symbol"],
                "company": item["company"],
                "shares": f"{item['shares']:.6f}",
                "buy_price": f"{item['buy_price']:.4f}",
                "current_price": f"{item['current_price']:.4f}",
                "invested_value": f"{item['invested_value']:.2f}",
                "market_value": f"{item['market_value']:.2f}",
                "gain_loss": f"{item['gain_loss']:.2f}",
                "gain_loss_pct": f"{item['gain_loss_pct']:.4f}",
                "price_source": item["price_source"],
            })

        writer.writerow({
            "timestamp": timestamp,
            "record_type": "PORTFOLIO_TOTAL",
            "symbol": "TOTAL",
            "company": "All holdings",
            "shares": "",
            "buy_price": "",
            "current_price": "",
            "invested_value": f"{totals['invested_value']:.2f}",
            "market_value": f"{totals['market_value']:.2f}",
            "gain_loss": f"{totals['gain_loss']:.2f}",
            "gain_loss_pct": f"{totals['gain_loss_pct']:.4f}",
            "price_source": "combined holdings",
        })

    print(f"\nPerformance log saved to: {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Track stock holdings and portfolio performance."
    )
    parser.add_argument(
        "--manual-prices",
        action="store_true",
        help="Ask for current prices instead of trying yfinance.",
    )
    parser.add_argument(
        "--ticker-file",
        default=str(TICKER_FILE),
        help="CSV file containing a Symbol column.",
    )
    parser.add_argument(
        "--output",
        default=str(SUMMARY_FILE),
        help="CSV file where performance history is appended.",
    )
    args = parser.parse_args()

    try:
        tickers = load_tickers(args.ticker_file)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Could not load ticker dataset: {error}")
        return 1

    print("\n" + "=" * 58)
    print("             STOCK PORTFOLIO TRACKER")
    print("=" * 58)
    print(f"Loaded {len(tickers)} ticker symbols from the supplied dataset.")

    positions = collect_portfolio(tickers)
    if not positions:
        print("No holdings were entered. Nothing to calculate.")
        return 0

    results = []
    for symbol, position in positions.items():
        company = tickers[symbol]
        manual_price = None

        if args.manual_prices:
            print(f"\nCurrent market price for {symbol} ({company})")
            manual_price = read_positive_number("Enter current price per share: ")

        result = calculate_position(
            symbol,
            position,
            company,
            manual_price=manual_price,
        )
        results.append(result)

    totals = display_report(results)

    try:
        save_summary(results, totals, args.output)
    except OSError as error:
        print(f"Could not save CSV report: {error}")
        return 1

    print("\nNote: This is a tracking/educational tool, not investment advice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
