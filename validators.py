"""
Validation helpers for the /tick payload.
Each function raises ValueError with a human-readable message on bad input.
"""


def _is_number(value):
    # bool is a subclass of int in Python, so exclude it explicitly
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def _require_list(payload, key, label, allow_empty):
    if key not in payload:
        raise ValueError(f"{label} is required")
    value = payload[key]
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if not allow_empty and len(value) == 0:
        raise ValueError(f"{label} must be a non-empty list")
    return value


def _validate_items(items, label, schema):
    """schema maps field name -> (checker, type description)."""
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{label}[{i}] must be an object")
        for field, (checker, desc) in schema.items():
            if field not in item:
                raise ValueError(f"{label}[{i}] is missing '{field}'")
            if not checker(item[field]):
                raise ValueError(f"{label}[{i}].{field} must be {desc}")


POSITION_SCHEMA = {
    "ticker": (_is_nonempty_str, "a non-empty string"),
    "quantity": (_is_number, "a number"),
    "purchase_price": (lambda v: _is_number(v) and v >= 0, "a non-negative number"),
}

SUMMARY_SCHEMA = {
    "ticker": (_is_nonempty_str, "a non-empty string"),
    "current_price": (lambda v: _is_number(v) and v >= 0, "a non-negative number"),
    "category": (_is_nonempty_str, "a non-empty string"),
}

HISTORY_SCHEMA = {
    "ticker": (_is_nonempty_str, "a non-empty string"),
    "price": (lambda v: _is_number(v) and v >= 0, "a non-negative number"),
    "day": (_is_nonempty_str, "a non-empty string"),
}


def validate_tick_payload(payload):
    """Validate the full /tick payload. Raises ValueError if invalid."""
    if not isinstance(payload, dict):
        raise ValueError("body must be a JSON object")

    positions = _require_list(payload, "Positions", "Positions", allow_empty=True)
    summary = _require_list(payload, "Market_Summary", "Market Summary", allow_empty=False)
    history = _require_list(payload, "market_history", "market history", allow_empty=True)

    _validate_items(positions, "Positions", POSITION_SCHEMA)
    _validate_items(summary, "Market_Summary", SUMMARY_SCHEMA)
    _validate_items(history, "market_history", HISTORY_SCHEMA)
