import pandas as pd
sales = pd.read_csv("data/restaurant_sales_test.csv")
print(sales.head())

is_duplicate = sales.duplicated(subset=['order_id', "line_id"], keep="first")

duplicate_rows = sales[is_duplicate]
print(duplicate_rows)

duplicate_total = duplicate_rows["line_total"].sum()
print(f"Sales from duplicate rows: ${duplicate_total:.2f}")

is_missing_price = sales["unit_price"].isna()
print(sales[is_missing_price]) 

sales["expected_total"] = (sales["quantity"] * sales["unit_price"]).round(2)
print(sales[["item", "quantity", "unit_price", "line_total", "expected_total"]])

