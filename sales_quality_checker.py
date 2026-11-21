import pandas as pd
def normalize_header(header):
    words = header.strip().lower().replace("-", " ").split()
    return "_".join(words)

SALES_HEADER_ALIASES = {
    "order_id": {"invoice_number", "receipt_id"},
    "line_id": {"invoice_line", "line_number"},
    "quantity": {"qty", "cases_sold"},
    "unit_price": {"price_per_unit", "price_per_case"},
    "line_total": {"line_subtotal", "extended_amount"},
    }

def suggest_column_matches(headers):
    matches = {}

    for field, aliases in SALES_HEADER_ALIASES.items():
        matches[field] = []

        for header in headers:
            normalized = normalize_header(header)
            if normalized == field or normalized in aliases:
                matches[field].append(header)

    return matches

def map_sales_columns(sales_data):
    matches = suggest_column_matches(sales_data.columns)
    rename_map = {}

    for field, candidates in matches.items():
        if len(candidates) == 1:
            rename_map[candidates[0]] = field
        elif len(candidates) > 1:
            choices = ", ".join(candidates)
            raise ValueError(f"Multiple columns match for {field}: {choices}")
    return sales_data.rename(columns=rename_map)

issue_labels = {
    "duplicate": "Duplicate row",
    "missing_price": "Missing unit price",
    "wrong_total": "Incorrect total"
}

def describe_issues(row):
    labels = []
    for column, label in issue_labels.items():
        if row[column]:
            labels.append(label)
    return " | ".join(labels)

def build_review_table(sales, is_duplicate, is_missing_price, is_wrong_total):
    needs_review = is_duplicate | is_missing_price | is_wrong_total
    reviewed_rows = sales.loc[needs_review].copy()

    reviewed_rows["duplicate"] = is_duplicate
    reviewed_rows["missing_price"] = is_missing_price
    reviewed_rows["wrong_total"] = is_wrong_total

    labels = [describe_issues(row) for _, row in reviewed_rows.iterrows()]
    reviewed_rows.insert(0, "issues", labels)
    return reviewed_rows

def find_duplicate_flags(sales_data):
    return sales_data.duplicated(subset=['order_id', "line_id"], keep="first")

def check_line_totals(sales_data):
    expected_total = (sales_data["quantity"] * sales_data["unit_price"]).round(2)
    difference = (sales_data["line_total"] - expected_total).round(2)
    is_wrong_total = difference.notna() & (difference != 0)
    return expected_total, difference, is_wrong_total

def run_sales_checks(sales_data):
    required_columns = ["order_id", "line_id", "item", "quantity", "unit_price", "line_total"]
    missing_columns = [column for column in required_columns if column not in sales_data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    checked_sales = sales_data.copy()

    is_duplicate = find_duplicate_flags(checked_sales)
    is_missing_price = checked_sales["unit_price"].isna()
    expected_total, difference, is_wrong_total = check_line_totals(checked_sales)

    checked_sales["expected_total"] = expected_total
    checked_sales["difference"] = difference

    return checked_sales, is_duplicate, is_missing_price, is_wrong_total

def main():
    sales = pd.read_csv("data/restaurant_sales_stress_test.csv") 
    print("Headers after mapping:", list(sales.columns))

    for header in sales.columns:
        print(f"{header!r} -> {normalize_header(header)!r}")

    sales, is_duplicate, is_missing_price, is_wrong_total = run_sales_checks(sales)
    print(sales.head())
    duplicate_rows = sales[is_duplicate]

    is_duplicate = find_duplicate_flags(sales)

    print()
    print(duplicate_rows)

    duplicate_total = duplicate_rows["line_total"].sum()

    print(f"Sales from duplicate rows: ${duplicate_total:,.2f}")

    is_missing_price = sales["unit_price"].isna()
    print()
    print(sales[is_missing_price])


    expected_total, difference, is_wrong_total = check_line_totals(sales)
    sales["expected_total"] = expected_total
    sales["difference"] = difference
    print()
    print(sales[["item", "quantity", "unit_price", "line_total", "expected_total"]])

    print()
    print(sales.loc[is_wrong_total, ["item", "line_total", "expected_total", "difference"]])

    needs_review = is_duplicate | is_missing_price | is_wrong_total
    print()
    print(f"Total rows checked: {len(sales):,}")
    print(f"Total rows needing review: {needs_review.sum():,}")


    is_wrong_original = is_wrong_total & ~is_duplicate
    total_correction = sales.loc[is_wrong_original, "difference"].sum()

    known_overstatement = duplicate_total + total_correction
    print (f"Known overstatement of sales: ${known_overstatement:,.2f}")

    reported_sales = sales["line_total"].sum()
    adjusted_sales = reported_sales - known_overstatement
    print(f"Reported sales: ${reported_sales:,.2f}")
    print(f"Sales after known corrections: ${adjusted_sales:,.2f}")

    review_rows = build_review_table(sales, is_duplicate, is_missing_price, is_wrong_total)
    review_rows.to_csv("rows_needing_review.csv", index=False)

if __name__ == "__main__":
    main()


