"""
Business layer: trading analysis logic. No Flask imports here.
"""


def analyze_tick(payload: dict) -> dict:
    """
    Join Positions with Market_Summary by ticker and compute unrealized P&L:
        (current_price - purchase_price) * quantity, summed over matched positions.
    Positions with no matching ticker in Market_Summary are skipped.
    """
    current_prices = {
        row["ticker"]: float(row["current_price"])
        for row in payload["Market_Summary"]
    }

    positions_evaluated = 0
    unrealized_pnl = 0.0
    details = []

    for pos in payload["Positions"]:
        ticker = pos["ticker"]
        if ticker not in current_prices:
            continue

        quantity = float(pos["quantity"])
        cost = float(pos["purchase_price"])
        price = current_prices[ticker]
        pnl = (price - cost) * quantity

        positions_evaluated += 1
        unrealized_pnl += pnl
        details.append({
            "ticker": ticker,
            "quantity": quantity,
            "purchase_price": cost,
            "current_price": price,
            "unrealized_pnl": pnl,
        })

    return {
        "result": "success",
        "summary": {
            "positions_evaluated": positions_evaluated,
            "unrealized_pnl": unrealized_pnl,
        },
        "positions": details,
        "decisions": [],  # placeholder for Part 3 trade logic
    }
